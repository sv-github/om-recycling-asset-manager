# Development Guide

## Development Environment

The application is designed to be developed using Docker.

The goal is to maintain the same development environment at every development
location.

## Requirements

- Windows 10/11
- Git
- Docker Desktop
- Docker Compose

Node.js and Python runtimes are provided by the project containers.

## Project Directory

Recommended location:

C:\Projects\om-recycling-asset-manager

## Basic Workflow

Before starting work:

    git pull

Start the development environment:

    docker compose up -d

Check running containers:

    docker compose ps

Stop the development environment:

    docker compose down

After making changes:

    git status
    git add .
    git commit -m "Describe the change"
    git push

## Development Rules

1. Do not modify the production database from the development environment.
2. Database structure changes must use migrations.
3. Secrets must never be committed to Git.
4. Changes should be committed in logical stages.
5. Major milestones receive version tags.