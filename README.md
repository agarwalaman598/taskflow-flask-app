# Task Management Web Application

A comprehensive Flask-based task management application built with PostgreSQL, featuring Object-Oriented Programming principles, REST API endpoints, and a modern web interface.

## 🚀 Features

### Core Functionality
- **Complete CRUD Operations**: Create, Read, Update, and Delete tasks
- **User Authentication**: Secure user registration and login system
- **Task Management**: Set priorities, due dates, and track task status
- **Advanced Filtering**: Filter tasks by status, priority, and search functionality
- **Dashboard Analytics**: Visual statistics and task insights

### Technical Features
- **Object-Oriented Design**: Clean class hierarchy with Task, User, and DatabaseHandler classes
- **PostgreSQL Database**: Robust database with proper schema and relationships
- **REST API**: Full REST endpoints returning JSON responses
- **Complex SQL Queries**: Implemented SELECT, JOIN, and GROUP BY operations
- **Responsive Design**: Mobile-friendly interface using Bootstrap 5
- **Real-time Updates**: AJAX-powered task status toggling

## 🛠 Tech Stack

### Backend
- **Python 3.8+**
- **Flask** - Web framework
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL** - Primary database
- **Flask-Login** - User session management
- **Werkzeug** - Password hashing and security

### Frontend
- **HTML5** - Semantic markup
- **Bootstrap 5** - Responsive UI framework
- **Vanilla JavaScript** - Client-side interactivity
- **Font Awesome** - Icons
- **Jinja2** - Template engine

### Database Schema
```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tasks table
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    priority VARCHAR(10) DEFAULT 'medium',
    due_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX idx_task_user_status ON tasks(user_id, status);
CREATE INDEX idx_task_user_priority ON tasks(user_id, priority);
CREATE INDEX idx_task_due_date ON tasks(due_date);
