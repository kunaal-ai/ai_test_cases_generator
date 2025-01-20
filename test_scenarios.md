# Test Scenarios for User Login Feature

## Successful User Login
User is able to successfully log in with valid credentials

### TC_001: Successful Login
**Priority:** High
**Type:** Positive

**Preconditions:**
- User is registered
- User is on Login page
- User has valid credentials

**Steps:**
1. Enter valid email
2. Enter valid password
3. Click on 'Log in' button

**Expected Results:**
- User is logged in
- User is redirected to homepage

---
## Failed User Login
User enters invalid credentials and fails to log in

### TC_002: Failed Login with Invalid Password
**Priority:** High
**Type:** Negative

**Preconditions:**
- User is registered
- User is on Login page

**Steps:**
1. Enter valid email
2. Enter invalid password
3. Click on 'Log in' button

**Expected Results:**
- Login attempt is unsuccessful
- An error message is displayed

---
### TC_003: Failed Login with Invalid Email
**Priority:** Medium
**Type:** Negative

**Preconditions:**
- User is on Login page

**Steps:**
1. Enter invalid email
2. Enter any password
3. Click on 'Log in' button

**Expected Results:**
- Login attempt is unsuccessful
- An error message is displayed

---
## Account Lockout
User's account gets temporarily locked after 3 failed login attempts

### TC_004: Account Lockout after 3 Failed Attempts
**Priority:** High
**Type:** Negative

**Preconditions:**
- User is registered
- User is on Login page

**Steps:**
1. Enter valid email
2. Enter invalid password
3. Click on 'Log in' button
4. Repeat the previous 2 steps 2 more times

**Expected Results:**
- After 3rd failed attempt, account is locked
- An account locked message is displayed

---
## Password Recovery
User is able to recover password using the 'Forgot Password' feature

### TC_005: Successful Password Recovery
**Priority:** Medium
**Type:** Positive

**Preconditions:**
- User is registered
- User is on Login page

**Steps:**
1. Click on 'Forgot Password'
2. Enter registered email
3. Click on 'Submit'
4. Open email
5. Click on password reset link
6. Enter new password
7. Confirm new password
8. Click on 'Reset Password'

**Expected Results:**
- Password reset email is sent
- User is able to set a new password
- User is redirected to login page

---
