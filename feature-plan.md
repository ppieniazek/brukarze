# Brukarze App - Feature Plan

## Project Stack & Overview

- Backend: Django with Daphne for ASGI.
- Frontend: Plain HTML templates with Pico.css for styling.
- Interactivity: Datastar.js (datastar-py) for dynamic, real-time UI updates.
- Language: Codebase in English, website in Polish.

## Development Workflow

- Implement one feature at a time.
- Provide code changes in concise snippets.
- Accompany code with clear instructions.

## Current Status: Authentication Complete

- A custom workers.User model is implemented (no email required).
- Roles: Szef and Brygadzista (Django Groups).
- Logic for initial Szef registration and subsequent user login is complete.

## Finalized Data Models & Logic

- workers.User (Custom User Model):
  - Inherits from AbstractUser.
  - Linked OneToOneField to a Worker record.
- workers.Worker:
  - user: OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
  - first_name, last_name: CharField
  - hourly_wage: PositiveIntegerField
  - is_active: BooleanField(default=True)
- workers.Brigade:
  - name: CharField
  - owner: ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
  - workers: ManyToManyField(Worker)
- workers.HourEntry:
  - worker: ForeignKey(Worker, on_delete=models.CASCADE)
  - date: DateField
  - hours: DecimalField
  - last_edited_by: ForeignKey(User, on_delete=models.SET_NULL, null=True)
- workers.Advance & workers.Expense:
  - worker: ForeignKey(Worker) (Advance only)
  - description: CharField (Expense only)
  - amount: DecimalField
  - is_paid: BooleanField(default=False)
  - created_by: ForeignKey(User, on_delete=models.PROTECT)
  - paid_at: DateTimeField(null=True, blank=True)
- Business Rules:
  - Deactivating a Brygadzista's User account does not deactivate the Worker record (degradation).
  - Deactivating a Worker record deactivates the linked User account.
  - Deleting a Worker record deletes the linked User account.
  - Only Szef can mark Advance/Expense as paid.
  - Brygadzista can only delete unpaid Advance/Expense entries they created.

## Feature Roadmap

### Role: Szef

- Dashboard: Grid of cards with statistics and links.
- Worker Management: Full CRUD for Worker records.
- Brygadzista Management: Promote a Worker to Brygadzista (create User account) and degrade them (deactivate User account).
- Brigade Management: CRUD for custom brigades.
- Hours Management: View/edit hours for all workers with filters.
- Advances & Expenses Management: View all entries and mark as "Paid".

### Role: Brygadzista

- Dashboard: Interactive table to manage hours for their brigades.
- Brigade Management: Add/remove workers from their primary brigade.
- Advances Management: Create/view/delete their own unpaid Advance entries.
- Expenses Management: Create/view/delete their own unpaid Expense entries.
