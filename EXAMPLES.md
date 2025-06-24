# Voice Command Examples

This document provides real-world examples of voice commands and their effects on markdown files.

## 🎯 **Task Management Commands**

### Example 1: Marking Tasks Complete

**Voice Command:** *"Mark the second task as complete"*

**Before:**
```markdown
# TODO List
- [ ] Review project proposal
- [ ] Attend team meeting
- [ ] Submit report
```

**After:**
```markdown
# TODO List
- [ ] Review project proposal
- [x] Attend team meeting
- [ ] Submit report
```

### Example 2: Adding New Tasks

**Voice Command:** *"Add a new task about calling the dentist under personal tasks"*

**Before:**
```markdown
## Personal Tasks
- [ ] Buy groceries
- [ ] Exercise for 30 minutes
```

**After:**
```markdown
## Personal Tasks
- [ ] Buy groceries
- [ ] Exercise for 30 minutes
- [ ] Call the dentist
```

### Example 3: Moving Tasks Between Sections

**Voice Command:** *"Move the grocery shopping task to the urgent section"*

**Before:**
```markdown
## Personal Tasks
- [ ] Buy groceries
- [ ] Read book

## Urgent
- [ ] Pay rent
```

**After:**
```markdown
## Personal Tasks
- [ ] Read book

## Urgent
- [ ] Pay rent
- [ ] Buy groceries
```

## 📝 **Content Editing Commands**

### Example 4: Changing Headings

**Voice Command:** *"Change the heading from TODO to Completed Tasks"*

**Before:**
```markdown
# TODO
- [x] Finish presentation
- [x] Send emails
```

**After:**
```markdown
# Completed Tasks
- [x] Finish presentation
- [x] Send emails
```

### Example 5: Adding Bullet Points

**Voice Command:** *"Add a bullet point about the quarterly review meeting under work notes"*

**Before:**
```markdown
## Work Notes
- Team standup at 9 AM
- Code review session
```

**After:**
```markdown
## Work Notes
- Team standup at 9 AM
- Code review session
- Quarterly review meeting
```

### Example 6: Updating Content

**Voice Command:** *"Change the meeting time from 2 PM to 3 PM"*

**Before:**
```markdown
## Schedule
- Team meeting at 2 PM
- Client call at 4 PM
```

**After:**
```markdown
## Schedule
- Team meeting at 3 PM
- Client call at 4 PM
```

## 🏗️ **Structure Modification Commands**

### Example 7: Creating New Sections

**Voice Command:** *"Create a new section called Ideas below the tasks"*

**Before:**
```markdown
# Daily Planner

## Tasks
- [ ] Review documents
- [ ] Call client

## Notes
- Meeting went well
```

**After:**
```markdown
# Daily Planner

## Tasks
- [ ] Review documents
- [ ] Call client

## Ideas
- 

## Notes
- Meeting went well
```

### Example 8: Reordering Sections

**Voice Command:** *"Move the Ideas section to the top"*

**Before:**
```markdown
## Tasks
- [ ] Complete project

## Notes
- Important meeting today

## Ideas
- New product feature
```

**After:**
```markdown
## Ideas
- New product feature

## Tasks
- [ ] Complete project

## Notes
- Important meeting today
```

### Example 9: Removing Content

**Voice Command:** *"Remove the completed tasks section"*

**Before:**
```markdown
## Active Tasks
- [ ] Write report
- [ ] Review code

## Completed Tasks
- [x] Send emails
- [x] Update documentation

## Notes
- Good progress today
```

**After:**
```markdown
## Active Tasks
- [ ] Write report
- [ ] Review code

## Notes
- Good progress today
```

## 📊 **Advanced Editing Examples**

### Example 10: Working with Obsidian Links

**Voice Command:** *"Add a link to the project planning note in the first task"*

**Before:**
```markdown
## Project Tasks
- [ ] Review requirements
- [ ] Create timeline
```

**After:**
```markdown
## Project Tasks
- [ ] Review requirements [[Project Planning]]
- [ ] Create timeline
```

### Example 11: Managing Tags

**Voice Command:** *"Add the urgent tag to the deadline task"*

**Before:**
```markdown
## This Week
- [ ] Submit proposal deadline Friday
- [ ] Team building event
```

**After:**
```markdown
## This Week
- [ ] Submit proposal deadline Friday #urgent
- [ ] Team building event
```

### Example 12: Complex Restructuring

**Voice Command:** *"Organize all incomplete tasks by priority and move completed ones to the bottom"*

**Before:**
```markdown
# Tasks
- [x] Email sent
- [ ] High priority: Submit report
- [ ] Low priority: Organize desk
- [x] Meeting completed
- [ ] Medium priority: Review code
```

**After:**
```markdown
# Tasks

## High Priority
- [ ] Submit report

## Medium Priority
- [ ] Review code

## Low Priority
- [ ] Organize desk

## Completed
- [x] Email sent
- [x] Meeting completed
```

## 🎤 **Live Transcription Examples**

### Example 13: Meeting Notes

**Voice Input:** *"Meeting started at 2 PM with Alice Bob and Charlie. Main topics discussed were project timeline, budget allocation, and team responsibilities. Alice will handle frontend development, Bob will manage backend, Charlie will oversee testing. Next meeting scheduled for Friday."*

**Output:**
```markdown
# Meeting Notes

**Date:** 2025-06-24
**Time:** 2:00 PM
**Attendees:** Alice, Bob, Charlie

## Main Topics
- Project timeline
- Budget allocation  
- Team responsibilities

## Assignments
- **Alice:** Frontend development
- **Bob:** Backend management
- **Charlie:** Testing oversight

## Next Steps
- Next meeting: Friday
```

### Example 14: Quick Notes

**Voice Input:** *"Remember to buy milk eggs and bread from the store. Also need to call the bank about the account issue and schedule car maintenance for next week."*

**Output:**
```markdown
# Quick Notes

## Shopping List
- Milk
- Eggs
- Bread

## To Do
- [ ] Call bank about account issue
- [ ] Schedule car maintenance for next week
```

## 🔧 **Command-Line Usage Examples**

### Basic Commands

```bash
# Edit a specific file
python main.py --file notes.md

# Preview changes without applying
python main.py --file notes.md --dry-run

# Use enter-to-stop recording
python main.py --file notes.md --enter-stop

# Enable verbose output for debugging
python main.py --file notes.md --verbose
```

### Model Selection

```bash
# Use faster model for simple edits
python main.py --whisper-model tiny --file simple-notes.md

# Use most accurate model for complex commands
python main.py --whisper-model large --file complex-document.md
```

### Special Modes

```bash
# Interactive menu interface
python main.py --interactive

# Live transcription streaming
python main.py --live

# Transcript only (no GPT processing)
python main.py --transcript-only

# Undo recent changes
python main.py --undo notes.md
```

## 💡 **Tips for Effective Voice Commands**

### ✅ **Best Practices**

1. **Be Specific:** Reference exact sections, tasks, or content
2. **Use Context:** Mention section names and relative positions
3. **Speak Clearly:** Pause between commands, avoid filler words
4. **Be Concise:** One clear action per command
5. **Use Natural Language:** Commands can be conversational

### ❌ **Common Pitfalls**

1. **Too Vague:** "Change something" or "Fix this"
2. **Multiple Actions:** "Add a task and also remove that section and change the heading"
3. **Unclear References:** "Move that thing to the other place"
4. **Background Noise:** Recording in noisy environments
5. **Speaking Too Fast:** Rushing through complex commands

### 🎯 **Command Templates**

**Adding Content:**
- "Add [content] to [section]"
- "Create a new [item type] called [name]"
- "Insert [content] after [reference point]"

**Modifying Content:**
- "Change [old content] to [new content]"
- "Mark [task] as [status]"
- "Update [field] to [value]"

**Moving Content:**
- "Move [item] to [destination]"
- "Reorder [section] by [criteria]"
- "Place [item] before/after [reference]"

**Removing Content:**
- "Remove [item] from [section]"
- "Delete the [content type]"
- "Clear [section]"

---

> **💡 Pro Tip:** Start with simple commands and gradually work up to more complex editing as you get comfortable with the voice interface. Use `--dry-run` mode to preview changes before applying them!