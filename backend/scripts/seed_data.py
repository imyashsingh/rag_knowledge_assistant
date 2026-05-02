#!/usr/bin/env python3
"""
Seed sample data script for DocuMind backend
"""

import os
import sys
from pathlib import Path

# Add app directory to Python path
app_dir = Path(__file__).parent.parent
sys.path.insert(0, str(app_dir))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.repositories.workspace_repo import WorkspaceRepository
from app.db.repositories.user_repo import UserRepository
from app.db.repositories.document_repo import DocumentRepository
from app.db.repositories.chunk_repo import ChunkRepository
from app.core.security import hash_password
from app.rag.embeddings import generate_embedding
from app.utils.logger import setup_logging, get_logger


def create_sample_workspace(db: Session, name: str):
    """Create a sample workspace"""
    workspace_repo = WorkspaceRepository(db)
    
    workspace = workspace_repo.get_by_name(name)
    if not workspace:
        workspace = workspace_repo.create_workspace(name)
    
    return workspace


def create_sample_user(db: Session, email: str, password: str, workspace_id: int):
    """Create a sample user"""
    user_repo = UserRepository(db)
    
    user = user_repo.get_by_email(email)
    if not user:
        user = user_repo.create_user(
            email=email,
            password=hash_password(password),
            workspace_id=workspace_id
        )
    
    return user


def create_sample_document(db: Session, title: str, content: str, workspace_id: int):
    """Create a sample document with chunks"""
    doc_repo = DocumentRepository(db)
    chunk_repo = ChunkRepository(db)
    
    # Create document
    document = doc_repo.create_document(
        title=title,
        filename=f"{title.lower().replace(' ', '_')}.txt",
        content_type="text/plain",
        workspace_id=workspace_id
    )
    
    # Split content into chunks
    chunk_size = 500
    chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
    
    # Create chunks with embeddings
    for i, chunk_text in enumerate(chunks):
        embedding = generate_embedding(chunk_text)
        chunk_repo.create_chunk(
            text=chunk_text,
            embedding=embedding,
            workspace_id=workspace_id,
            document_id=document.id,
            chunk_index=i
        )
    
    return document


def seed_sample_data():
    """Seed sample data for testing"""
    logger = get_logger(__name__)
    
    try:
        logger.info("Starting sample data seeding...")
        
        db = SessionLocal()
        try:
            # Create sample workspace
            workspace = create_sample_workspace(db, "Sample Workspace")
            logger.info(f"Created workspace: {workspace.name}")
            
            # Create sample users
            users_data = [
                ("admin@documind.com", "Admin123!"),
                ("user1@documind.com", "User123!"),
                ("user2@documind.com", "User123!")
            ]
            
            users = []
            for email, password in users_data:
                user = create_sample_user(db, email, password, workspace.id)
                users.append(user)
                logger.info(f"Created user: {email}")
            
            # Sample documents content
            documents_data = [
                {
                    "title": "Introduction to Machine Learning",
                    "content": """
Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. It focuses on developing computer programs that can access data and use it to learn for themselves.

The process of learning begins with observations or data, such as examples, direct experience, or instruction, in order to look for patterns in data and make better decisions in the future based on the examples that we provide. The primary aim is to allow the computers to learn automatically without human intervention or assistance and adjust actions accordingly.

Some machine learning methods include supervised learning, unsupervised learning, and reinforcement learning. Supervised learning algorithms build a mathematical model of a set of data that contains both the inputs and the desired outputs.
                    """.strip()
                },
                {
                    "title": "Deep Learning Fundamentals",
                    "content": """
Deep learning is a subset of machine learning that uses neural networks with multiple layers to progressively extract higher-level features from raw input. For example, in image processing, lower layers may identify edges, while higher layers may identify concepts relevant to a human such as digits, letters, or faces.

Neural networks are a series of algorithms that endeavor to recognize underlying relationships in a set of data through a process that mimics the way the human brain operates. Neural networks can adapt to changing input; so the network generates the best possible result without needing to redesign the output criteria.

The concept of deep learning is not new, but recent advancements in computing power and data availability have made it more practical. Deep learning has been responsible for breakthroughs in computer vision, natural language processing, and speech recognition.
                    """.strip()
                },
                {
                    "title": "Natural Language Processing Overview",
                    "content": """
Natural Language Processing (NLP) is a branch of artificial intelligence that helps computers understand, interpret and manipulate human language. NLP draws from many disciplines, including computer science and computational linguistics, in its pursuit to fill the gap between human communication and computer understanding.

The development of NLP applications is challenging because computers traditionally require humans to speak to them in a programming language that is precise, unambiguous, and highly structured, while human speech tends to be the opposite. NLP enables computers to understand natural language as humans do.

Key NLP tasks include speech recognition, natural language understanding, natural language generation, and machine translation. Modern NLP systems often use deep learning techniques, particularly transformer architectures like BERT and GPT.
                    """.strip()
                }
            ]
            
            # Create sample documents
            documents = []
            for doc_data in documents_data:
                document = create_sample_document(
                    db, 
                    doc_data["title"], 
                    doc_data["content"], 
                    workspace.id
                )
                documents.append(document)
                logger.info(f"Created document: {doc_data['title']}")
            
            # Summary
            logger.info("Sample data seeding completed successfully!")
            logger.info(f"Created:")
            logger.info(f"  - 1 workspace: {workspace.name}")
            logger.info(f"  - {len(users)} users")
            logger.info(f"  - {len(documents)} documents")
            
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Failed to seed sample data: {str(e)}")
        return False


def clear_sample_data():
    """Clear all sample data - DANGEROUS!"""
    logger = get_logger(__name__)
    
    # Safety check
    if os.getenv("ENVIRONMENT") == "production":
        logger.error("Data clearing not allowed in production environment")
        return False
    
    response = input("WARNING: This will delete ALL data. Are you sure? (yes/no): ")
    if response.lower() != "yes":
        logger.info("Data clearing cancelled")
        return False
    
    try:
        logger.info("Clearing sample data...")
        
        db = SessionLocal()
        try:
            # Delete in order of dependencies
            chunk_repo = ChunkRepository(db)
            doc_repo = DocumentRepository(db)
            user_repo = UserRepository(db)
            workspace_repo = WorkspaceRepository(db)
            
            # Get all workspaces and delete their data
            workspaces = workspace_repo.get_all()
            for workspace in workspaces:
                logger.info(f"Clearing workspace: {workspace.name}")
                
                # Delete chunks
                chunks = chunk_repo.get_workspace_chunks(workspace.id)
                for chunk in chunks:
                    chunk_repo.delete(chunk.id)
                
                # Delete documents
                documents = doc_repo.get_by_workspace(workspace.id)
                for document in documents:
                    doc_repo.delete(document.id)
                
                # Delete users
                users = user_repo.get_workspace_users(workspace.id)
                for user in users:
                    user_repo.delete(user.id)
                
                # Delete workspace
                workspace_repo.delete(workspace.id)
            
            logger.info("Sample data cleared successfully")
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Failed to clear sample data: {str(e)}")
        return False


if __name__ == "__main__":
    # Setup logging
    setup_logging(log_level="INFO")
    
    logger = get_logger(__name__)
    logger.info("Sample data seeding script started")
    
    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "seed":
            success = seed_sample_data()
        elif command == "clear":
            success = clear_sample_data()
        else:
            logger.error(f"Unknown command: {command}")
            logger.info("Available commands: seed, clear")
            sys.exit(1)
    else:
        # Default: seed data
        success = seed_sample_data()
    
    if success:
        logger.info("Script completed successfully")
        sys.exit(0)
    else:
        logger.error("Script failed")
        sys.exit(1)
