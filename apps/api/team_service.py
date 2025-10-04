import os
import secrets
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from models import User, Team, Role, TeamMembership, TeamInvitation, Permission
from email_service import EmailService
import json

logger = logging.getLogger(__name__)

class TeamService:
    """Service class for handling team management and RBAC operations"""
    
    # Default system roles and permissions
    SYSTEM_ROLES = {
        "owner": {
            "description": "Team owner with full access",
            "permissions": ["*"]  # All permissions
        },
        "admin": {
            "description": "Team administrator with most permissions",
            "permissions": [
                "agents:create", "agents:read", "agents:update", "agents:delete",
                "tasks:create", "tasks:read", "tasks:update", "tasks:delete",
                "team:read", "team:update", "team:invite", "team:manage_members",
                "billing:read", "billing:update"
            ]
        },
        "member": {
            "description": "Team member with basic permissions",
            "permissions": [
                "agents:create", "agents:read", "agents:update",
                "tasks:create", "tasks:read", "tasks:update",
                "team:read"
            ]
        },
        "viewer": {
            "description": "Team viewer with read-only access",
            "permissions": [
                "agents:read", "tasks:read", "team:read"
            ]
        }
    }
    
    @staticmethod
    def create_team(
        name: str,
        description: Optional[str],
        owner: User,
        db: Session
    ) -> Team:
        """Create a new team"""
        try:
            # Create team
            team = Team(
                name=name,
                description=description,
                owner_id=owner.id,
                settings={}
            )
            db.add(team)
            db.commit()
            db.refresh(team)
            
            # Add owner as team member with owner role
            owner_role = TeamService.get_or_create_role("owner", db)
            membership = TeamMembership(
                team_id=team.id,
                user_id=owner.id,
                role_id=owner_role.id,
                invited_by_id=owner.id
            )
            db.add(membership)
            db.commit()
            
            logger.info(f"Created team {team.name} with owner {owner.email}")
            return team
            
        except Exception as e:
            logger.error(f"Error creating team: {e}")
            raise
    
    @staticmethod
    def get_user_teams(user: User, db: Session) -> List[Team]:
        """Get all teams a user belongs to"""
        teams = db.query(Team).join(TeamMembership).filter(
            and_(
                TeamMembership.user_id == user.id,
                TeamMembership.is_active == True,
                Team.is_active == True
            )
        ).all()
        return teams
    
    @staticmethod
    def get_team_members(team_id: str, db: Session) -> List[Dict[str, Any]]:
        """Get all members of a team"""
        memberships = db.query(TeamMembership).join(User).join(Role).filter(
            and_(
                TeamMembership.team_id == team_id,
                TeamMembership.is_active == True
            )
        ).all()
        
        members = []
        for membership in memberships:
            members.append({
                "id": membership.id,
                "user_id": membership.user_id,
                "user_name": membership.user.name,
                "user_email": membership.user.email,
                "role_id": membership.role_id,
                "role_name": membership.role.name,
                "joined_at": membership.joined_at,
                "invited_by_id": membership.invited_by_id
            })
        
        return members
    
    @staticmethod
    def invite_user_to_team(
        team_id: str,
        invited_email: str,
        role_name: str,
        invited_by: User,
        db: Session
    ) -> TeamInvitation:
        """Invite a user to join a team"""
        try:
            # Check if team exists and user has permission
            team = db.query(Team).filter(Team.id == team_id).first()
            if not team:
                raise ValueError("Team not found")
            
            if not TeamService.has_permission(invited_by.id, team_id, "team:invite", db):
                raise ValueError("Insufficient permissions to invite users")
            
            # Check if user is already a member
            existing_membership = db.query(TeamMembership).filter(
                and_(
                    TeamMembership.team_id == team_id,
                    TeamMembership.user_id.in_(
                        db.query(User.id).filter(User.email == invited_email)
                    )
                )
            ).first()
            
            if existing_membership:
                raise ValueError("User is already a team member")
            
            # Check for pending invitation
            existing_invitation = db.query(TeamInvitation).filter(
                and_(
                    TeamInvitation.team_id == team_id,
                    TeamInvitation.invited_email == invited_email,
                    TeamInvitation.status == "pending"
                )
            ).first()
            
            if existing_invitation:
                raise ValueError("User already has a pending invitation")
            
            # Get role
            role = TeamService.get_or_create_role(role_name, db)
            
            # Create invitation
            token = secrets.token_urlsafe(32)
            expires_at = datetime.utcnow() + timedelta(days=7)
            
            invitation = TeamInvitation(
                team_id=team_id,
                invited_email=invited_email,
                role_id=role.id,
                invited_by_id=invited_by.id,
                token=token,
                expires_at=expires_at
            )
            
            # Check if user exists
            existing_user = db.query(User).filter(User.email == invited_email).first()
            if existing_user:
                invitation.invited_user_id = existing_user.id
            
            db.add(invitation)
            db.commit()
            db.refresh(invitation)
            
            # Send invitation email
            TeamService._send_invitation_email(invitation, team, db)
            
            logger.info(f"Invited {invited_email} to team {team.name}")
            return invitation
            
        except Exception as e:
            logger.error(f"Error inviting user to team: {e}")
            raise
    
    @staticmethod
    def accept_invitation(token: str, user: User, db: Session) -> bool:
        """Accept a team invitation"""
        try:
            invitation = db.query(TeamInvitation).filter(
                and_(
                    TeamInvitation.token == token,
                    TeamInvitation.status == "pending",
                    TeamInvitation.expires_at > datetime.utcnow()
                )
            ).first()
            
            if not invitation:
                raise ValueError("Invalid or expired invitation")
            
            # Check if user is the invited user or email matches
            if invitation.invited_user_id and invitation.invited_user_id != user.id:
                raise ValueError("Invitation is for a different user")
            
            if not invitation.invited_user_id and invitation.invited_email != user.email:
                raise ValueError("Invitation email does not match")
            
            # Create team membership
            membership = TeamMembership(
                team_id=invitation.team_id,
                user_id=user.id,
                role_id=invitation.role_id,
                invited_by_id=invitation.invited_by_id
            )
            db.add(membership)
            
            # Update invitation
            invitation.status = "accepted"
            invitation.accepted_at = datetime.utcnow()
            invitation.invited_user_id = user.id
            
            db.commit()
            
            logger.info(f"User {user.email} accepted invitation to team {invitation.team_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error accepting invitation: {e}")
            raise
    
    @staticmethod
    def decline_invitation(token: str, user: User, db: Session) -> bool:
        """Decline a team invitation"""
        try:
            invitation = db.query(TeamInvitation).filter(
                and_(
                    TeamInvitation.token == token,
                    TeamInvitation.status == "pending"
                )
            ).first()
            
            if not invitation:
                raise ValueError("Invalid invitation")
            
            invitation.status = "declined"
            invitation.declined_at = datetime.utcnow()
            invitation.invited_user_id = user.id if user else None
            
            db.commit()
            
            logger.info(f"Invitation {token} declined")
            return True
            
        except Exception as e:
            logger.error(f"Error declining invitation: {e}")
            raise
    
    @staticmethod
    def update_member_role(
        team_id: str,
        user_id: str,
        new_role_name: str,
        updated_by: User,
        db: Session
    ) -> bool:
        """Update a team member's role"""
        try:
            # Check permissions
            if not TeamService.has_permission(updated_by.id, team_id, "team:manage_members", db):
                raise ValueError("Insufficient permissions to update member roles")
            
            # Get membership
            membership = db.query(TeamMembership).filter(
                and_(
                    TeamMembership.team_id == team_id,
                    TeamMembership.user_id == user_id,
                    TeamMembership.is_active == True
                )
            ).first()
            
            if not membership:
                raise ValueError("Team membership not found")
            
            # Get new role
            new_role = TeamService.get_or_create_role(new_role_name, db)
            
            # Update role
            membership.role_id = new_role.id
            membership.updated_at = datetime.utcnow()
            
            db.commit()
            
            logger.info(f"Updated role for user {user_id} in team {team_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating member role: {e}")
            raise
    
    @staticmethod
    def remove_member(
        team_id: str,
        user_id: str,
        removed_by: User,
        db: Session
    ) -> bool:
        """Remove a member from a team"""
        try:
            # Check permissions
            if not TeamService.has_permission(removed_by.id, team_id, "team:manage_members", db):
                raise ValueError("Insufficient permissions to remove members")
            
            # Get membership
            membership = db.query(TeamMembership).filter(
                and_(
                    TeamMembership.team_id == team_id,
                    TeamMembership.user_id == user_id,
                    TeamMembership.is_active == True
                )
            ).first()
            
            if not membership:
                raise ValueError("Team membership not found")
            
            # Deactivate membership
            membership.is_active = False
            membership.updated_at = datetime.utcnow()
            
            db.commit()
            
            logger.info(f"Removed user {user_id} from team {team_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing member: {e}")
            raise
    
    @staticmethod
    def has_permission(
        user_id: str,
        team_id: str,
        permission: str,
        db: Session
    ) -> bool:
        """Check if user has a specific permission in a team"""
        try:
            # Get user's role in the team
            membership = db.query(TeamMembership).join(Role).filter(
                and_(
                    TeamMembership.user_id == user_id,
                    TeamMembership.team_id == team_id,
                    TeamMembership.is_active == True
                )
            ).first()
            
            if not membership:
                return False
            
            # Check if role has all permissions (owner)
            if "*" in (membership.role.permissions or []):
                return True
            
            # Check specific permission
            return permission in (membership.role.permissions or [])
            
        except Exception as e:
            logger.error(f"Error checking permission: {e}")
            return False
    
    @staticmethod
    def get_user_role_in_team(user_id: str, team_id: str, db: Session) -> Optional[Role]:
        """Get user's role in a specific team"""
        membership = db.query(TeamMembership).join(Role).filter(
            and_(
                TeamMembership.user_id == user_id,
                TeamMembership.team_id == team_id,
                TeamMembership.is_active == True
            )
        ).first()
        
        return membership.role if membership else None
    
    @staticmethod
    def get_or_create_role(role_name: str, db: Session) -> Role:
        """Get existing role or create if it doesn't exist"""
        role = db.query(Role).filter(Role.name == role_name).first()
        
        if not role:
            # Create role with default permissions
            role_data = TeamService.SYSTEM_ROLES.get(role_name, {
                "description": f"Custom role: {role_name}",
                "permissions": []
            })
            
            role = Role(
                name=role_name,
                description=role_data["description"],
                permissions=role_data["permissions"],
                is_system_role=role_name in TeamService.SYSTEM_ROLES
            )
            db.add(role)
            db.commit()
            db.refresh(role)
        
        return role
    
    @staticmethod
    def create_default_roles(db: Session):
        """Create default system roles"""
        for role_name, role_data in TeamService.SYSTEM_ROLES.items():
            existing_role = db.query(Role).filter(Role.name == role_name).first()
            if not existing_role:
                role = Role(
                    name=role_name,
                    description=role_data["description"],
                    permissions=role_data["permissions"],
                    is_system_role=True
                )
                db.add(role)
        
        db.commit()
        logger.info("Created default system roles")
    
    @staticmethod
    def _send_invitation_email(invitation: TeamInvitation, team: Team, db: Session):
        """Send team invitation email"""
        try:
            invitation_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/invite/{invitation.token}"
            
            variables = {
                "team_name": team.name,
                "inviter_name": invitation.invited_by.name or "Team Admin",
                "invitation_url": invitation_url,
                "role_name": invitation.role.name,
                "expires_at": invitation.expires_at.strftime("%B %d, %Y at %I:%M %p"),
                "app_name": "Agentic MicroSaaS"
            }
            
            EmailService.send_template_email(
                template_name="team_invitation",
                to_email=invitation.invited_email,
                variables=variables,
                user_id=invitation.invited_by_id,
                db=db
            )
            
        except Exception as e:
            logger.error(f"Error sending invitation email: {e}")
    
    @staticmethod
    def get_team_invitations(team_id: str, db: Session) -> List[TeamInvitation]:
        """Get all pending invitations for a team"""
        return db.query(TeamInvitation).filter(
            and_(
                TeamInvitation.team_id == team_id,
                TeamInvitation.status == "pending"
            )
        ).all()
    
    @staticmethod
    def cancel_invitation(invitation_id: str, cancelled_by: User, db: Session) -> bool:
        """Cancel a pending invitation"""
        try:
            invitation = db.query(TeamInvitation).filter(
                TeamInvitation.id == invitation_id
            ).first()
            
            if not invitation:
                raise ValueError("Invitation not found")
            
            # Check permissions
            if not TeamService.has_permission(cancelled_by.id, invitation.team_id, "team:manage_members", db):
                raise ValueError("Insufficient permissions to cancel invitation")
            
            invitation.status = "cancelled"
            invitation.updated_at = datetime.utcnow()
            
            db.commit()
            
            logger.info(f"Cancelled invitation {invitation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling invitation: {e}")
            raise
