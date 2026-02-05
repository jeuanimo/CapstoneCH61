# Member Invitation Workflow Guide

## Overview
This system allows you to create member accounts in the roster FIRST, then generate invitation codes for them to set their passwords.

## New Workflow

### Step 1: Create Member in Roster
1. Go to **Member Roster** (`/portal/roster/`)
2. Click **"Add New Member"**
3. Fill in all member information including:
   - Username (they'll use this to login)
   - Email
   - First Name, Last Name
   - Member Number
   - Other profile fields
4. Click **Save**
5. **IMPORTANT**: The system will automatically:
   - Create a user account with a random password
   - Generate an invitation code
   - Display the invitation code in a success message

### Step 2: Send Invitation Code
1. Copy the invitation code shown in the success message
2. Send it to the member via email (to the email address you entered)
3. Tell them to:
   - Go to the signup page
   - Enter the invitation code
   - Use the SAME username you created for them
   - Set their own password

### Step 3: Member Signs Up
When the member receives the invitation code:
1. They visit the signup page
2. They enter:
   - The invitation code you sent them
   - The username you created for them
   - Their desired password
   - Confirm password
3. The system will:
   - Recognize the existing account
   - Set their new password
   - Activate their account
   - Log them in

## Generate New Invitation Code

If a member loses their invitation code or needs a new one:

1. Go to **Member Roster**
2. Find the member in the table
3. Click the **ticket icon** (🎫) button in their row
4. A new invitation code will be generated and displayed
5. Send the new code to the member

## Key Features

### Automatic Invitation Creation
- When you create a member, an invitation code is automatically generated
- No need to manually create invitation codes separately
- Invitation codes are displayed immediately after member creation

### Duplicate Prevention
- The system checks if a user already exists with that username
- If they do, it updates their password instead of creating a duplicate
- Members can safely use their invitation code even if their account already exists

### Staff Controls
Staff members can:
- Create members with invitation codes
- Generate new invitation codes for existing members
- View all active and used invitation codes
- Delete invitation codes if needed

## Troubleshooting

### "Username already exists" error
- This means you're trying to create a member with a username that's already taken
- Choose a different username

### Member can't login after signup
- Verify they used the correct username (the one you created for them)
- Generate a new invitation code and have them sign up again
- Check that their account is active in the roster

### Lost invitation code
- Click the ticket icon (🎫) next to their name in the roster
- A new invitation code will be generated
- Send them the new code

## Best Practices

1. **Create members in batches**: Add all new members to the roster first
2. **Send invitations promptly**: Send invitation codes immediately after creating members
3. **Keep records**: Save invitation codes in case members need them resent
4. **Set expiration dates**: Invitation codes expire after a certain time for security
5. **Use clear usernames**: Choose usernames that members will remember

## Technical Details

- Invitation codes are 20 characters long
- Codes are case-sensitive
- Codes expire after 30 days (default)
- Each code can only be used once
- Codes are tied to specific email addresses
- System automatically links member numbers to profiles
