#!/usr/bin/env python3
"""
Task Management Script for AI Agent Project

This script helps manage and track tasks across different categories.
"""

import os
import sys
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


class TaskManager:
    def __init__(self, tasks_dir: str = None):
        self.tasks_dir = Path(
            tasks_dir) if tasks_dir else Path(__file__).parent
        self.status_icons = {
            '🆕': 'new',
            '🔄': 'in_progress',
            '✅': 'completed',
            '⏸️': 'paused',
            '❌': 'blocked'
        }

    def parse_task_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse a task markdown file and extract task information."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        tasks = []
        current_task = None

        lines = content.split('\n')
        for line in lines:
            # Match task headers
            task_match = re.match(r'^### (\d+)\. (.+)$', line)
            if task_match:
                if current_task:
                    tasks.append(current_task)

                current_task = {
                    'id': task_match.group(1),
                    'title': task_match.group(2),
                    'status': 'unknown',
                    'priority': 'unknown',
                    'estimated_time': 'unknown',
                    'description': '',
                    'subtasks': []
                }
                continue

            if current_task:
                # Match status
                status_match = re.match(r'^\*\*Status\*\*: (.+)$', line)
                if status_match:
                    status_text = status_match.group(1)
                    for icon, status in self.status_icons.items():
                        if icon in status_text:
                            current_task['status'] = status
                            break
                    continue

                # Match priority
                priority_match = re.match(r'^\*\*Priority\*\*: (.+)$', line)
                if priority_match:
                    current_task['priority'] = priority_match.group(1).lower()
                    continue

                # Match estimated time
                time_match = re.match(r'^\*\*Estimated Time\*\*: (.+)$', line)
                if time_match:
                    current_task['estimated_time'] = time_match.group(1)
                    continue

                # Match description
                desc_match = re.match(r'^\*\*Description\*\*: (.+)$', line)
                if desc_match:
                    current_task['description'] = desc_match.group(1)
                    continue

                # Match subtasks
                subtask_match = re.match(r'^- \[ \] (.+)$', line)
                if subtask_match:
                    current_task['subtasks'].append({
                        'title': subtask_match.group(1),
                        'completed': False
                    })
                    continue

                # Match completed subtasks
                completed_match = re.match(r'^- \[x\] (.+)$', line)
                if completed_match:
                    current_task['subtasks'].append({
                        'title': completed_match.group(1),
                        'completed': True
                    })
                    continue

        if current_task:
            tasks.append(current_task)

        return {
            'file': file_path.name,
            'category': file_path.stem,
            'tasks': tasks
        }

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks from all task files."""
        all_tasks = []

        for file_path in self.tasks_dir.glob('*.md'):
            if file_path.name == 'README.md':
                continue

            try:
                task_data = self.parse_task_file(file_path)
                all_tasks.append(task_data)
            except Exception as e:
                print(f"Error parsing {file_path}: {e}")

        return all_tasks

    def print_summary(self):
        """Print a summary of all tasks."""
        all_tasks = self.get_all_tasks()

        print("🔥 AI Agent Project - Task Summary")
        print("=" * 50)

        total_tasks = 0
        status_counts = {status: 0 for status in self.status_icons.values()}
        status_counts['unknown'] = 0

        priority_counts = {'high': 0, 'medium': 0, 'low': 0, 'unknown': 0}

        for category_data in all_tasks:
            category = category_data['category'].replace('_', ' ').title()
            tasks = category_data['tasks']

            print(f"\n📁 {category}")
            print("-" * 30)

            if not tasks:
                print("  No tasks found")
                continue

            for task in tasks:
                total_tasks += 1
                status = task['status'].strip()
                priority = task['priority'].strip()

                status_counts[status] += 1
                priority_counts[priority] += 1

                # Get status icon
                status_icon = '❓'
                for icon, stat in self.status_icons.items():
                    if stat == status:
                        status_icon = icon
                        break

                # Progress indicator for subtasks
                if task['subtasks']:
                    completed = sum(
                        1 for st in task['subtasks'] if st['completed'])
                    total_subtasks = len(task['subtasks'])
                    progress = f"({completed}/{total_subtasks})"
                else:
                    progress = ""

                print(f"  {status_icon} {task['title']} {progress}")
                print(
                    f"     Priority: {task['priority']}, Time: {task['estimated_time']}")

        print(f"\n📊 Overall Statistics")
        print("-" * 30)
        print(f"Total Tasks: {total_tasks}")

        print("\nBy Status:")
        for status, count in status_counts.items():
            if count > 0:
                icon = '❓'
                for ic, st in self.status_icons.items():
                    if st == status:
                        icon = ic
                        break
                print(f"  {icon} {status.replace('_', ' ').title()}: {count}")

        print("\nBy Priority:")
        for priority, count in priority_counts.items():
            if count > 0:
                print(f"  • {priority.title()}: {count}")

    def get_next_tasks(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get the next recommended tasks to work on."""
        all_tasks = self.get_all_tasks()

        recommended = []

        # Priority scoring
        priority_scores = {'high': 3, 'medium': 2, 'low': 1, 'unknown': 0}
        status_scores = {'new': 2, 'in_progress': 3, 'paused': 1,
                         'completed': 0, 'blocked': 0, 'unknown': 1}

        for category_data in all_tasks:
            for task in category_data['tasks']:
                if task['status'] in ['completed', 'blocked']:
                    continue

                score = priority_scores.get(
                    task['priority'], 0) + status_scores.get(task['status'], 0)

                recommended.append({
                    'category': category_data['category'],
                    'task': task,
                    'score': score
                })

        # Sort by score (highest first)
        recommended.sort(key=lambda x: x['score'], reverse=True)

        return recommended[:limit]

    def print_next_tasks(self, limit: int = 5):
        """Print the next recommended tasks."""
        next_tasks = self.get_next_tasks(limit)

        print(f"\n🎯 Next {limit} Recommended Tasks")
        print("=" * 40)

        for i, item in enumerate(next_tasks, 1):
            task = item['task']
            category = item['category'].replace('_', ' ').title()

            # Get status icon
            status_icon = '❓'
            for icon, stat in self.status_icons.items():
                if stat == task['status']:
                    status_icon = icon
                    break

            print(f"\n{i}. {status_icon} {task['title']}")
            print(f"   Category: {category}")
            print(
                f"   Priority: {task['priority']}, Time: {task['estimated_time']}")
            print(f"   Description: {task['description'][:100]}...")

            if task['subtasks']:
                completed = sum(
                    1 for st in task['subtasks'] if st['completed'])
                total = len(task['subtasks'])
                print(f"   Progress: {completed}/{total} subtasks completed")


def main():
    """Main function to run the task manager."""
    task_manager = TaskManager()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == 'summary':
            task_manager.print_summary()
        elif command == 'next':
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            task_manager.print_next_tasks(limit)
        else:
            print("Unknown command. Use 'summary' or 'next'")
    else:
        # Default: show summary and next tasks
        task_manager.print_summary()
        task_manager.print_next_tasks()


if __name__ == "__main__":
    main()
