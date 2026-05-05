const API_BASE = "https://crispy-disco-v664gqx6qgg5fpp5q-5000.app.github.dev/";

let selectedEmail = "";
let selectedUsername = "";
let selectedRole = "";

const emailPanel = document.getElementById("email-panel");
const loginPanel = document.getElementById("login-panel");
const registerPanel = document.getElementById("register-panel");
const mfaPanel = document.getElementById("mfa-panel");
const protectedPanel = document.getElementById("protected-panel");

const outputEl = document.getElementById("output");
const messageEl = document.getElementById("message");

const authStatusEl = document.getElementById("auth-status");
const roleStatusEl = document.getElementById("role-status");
const userStatusEl = document.getElementById("user-status");

const dashboardTitle = document.getElementById("dashboard-title");
const dashboardDescription = document.getElementById("dashboard-description");
const patientDashboard = document.getElementById("patient-dashboard");
const providerDashboard = document.getElementById("provider-dashboard");
const adminDashboard = document.getElementById("admin-dashboard");

const recordUsernameInput = document.getElementById("record-username");
const recordIdInput = document.getElementById("record-id");
const recordButton = document.getElementById("record-btn");
const recordAccessNote = document.getElementById("record-access-note");

const auditUsernameInput = document.getElementById("audit-username");

function showPanel(panel) {
  [emailPanel, loginPanel, registerPanel, mfaPanel, protectedPanel].forEach(
    (item) => item.classList.add("hidden")
  );

  panel.classList.remove("hidden");
}

function showMessage(message, type = "info") {
  messageEl.textContent = message;
  messageEl.className = `message ${type}`;
}

function showOutput(data) {
  outputEl.textContent = JSON.stringify(data, null, 2);
}

function showTextOutput(text) {
  outputEl.textContent = text;
}

function updateSession(authenticated, username = "", role = "") {
  authStatusEl.textContent = authenticated ? "Authenticated" : "Not signed in";
  roleStatusEl.textContent = role || "None selected";
  userStatusEl.textContent = username || "None";
}

function resetDashboards() {
  patientDashboard.classList.add("hidden");
  providerDashboard.classList.add("hidden");
  adminDashboard.classList.add("hidden");

  dashboardTitle.textContent = "Protected Record Access";
  dashboardDescription.textContent =
    "MFA is complete. Access is assigned based on the authenticated role.";

  recordUsernameInput.value = "";
  recordIdInput.value = "1";

  recordButton.disabled = false;
  recordButton.classList.remove("hidden");

  if (auditUsernameInput) {
    auditUsernameInput.value = "admin";
  }

  recordAccessNote.textContent =
    "Record access is assigned after MFA based on the authenticated user's role.";

  outputEl.textContent = "Responses will appear here.";
}

function assignRecordAccess(username, role) {
  recordUsernameInput.value = username;

  patientDashboard.classList.add("hidden");
  providerDashboard.classList.add("hidden");
  adminDashboard.classList.add("hidden");

  recordButton.classList.remove("hidden");

  if (role === "provider") {
    dashboardTitle.textContent = "Provider Dashboard";
    dashboardDescription.textContent =
      "MFA is complete. Provider access is verified for assigned protected records.";

    providerDashboard.classList.remove("hidden");

    recordIdInput.value = "1";
    recordButton.disabled = false;
    recordAccessNote.textContent =
      "Provider access granted. Assigned record ID 1 is Jane Doe's asthma record.";

    showOutput({
      role: "provider",
      access: "assigned_record_available",
      assigned_record_id: 1,
      patient: "Jane Doe",
      note: "Click Retrieve Protected Record to view the masked and tokenized record.",
    });

    return;
  }

  if (role === "admin") {
    dashboardTitle.textContent = "Admin Dashboard";
    dashboardDescription.textContent =
      "MFA is complete. Admin access is verified for audit log review only.";

    adminDashboard.classList.remove("hidden");

    if (auditUsernameInput) {
      auditUsernameInput.value = username;
    }

    recordIdInput.value = "1";
    recordButton.disabled = true;
    recordButton.classList.add("hidden");

    recordAccessNote.textContent =
      "Admin access is limited to audit logs. Admin users cannot retrieve patient records from this screen.";

    showOutput({
      role: "admin",
      access: "audit_logs_only",
      note: "Click View Audit Logs to review security events.",
    });

    return;
  }

  dashboardTitle.textContent = "Patient Dashboard";
  dashboardDescription.textContent =
    "MFA is complete. Patient access is verified.";

  patientDashboard.classList.remove("hidden");

  recordIdInput.value = "";
  recordButton.disabled = true;
  recordButton.classList.add("hidden");

  recordAccessNote.textContent =
    "No appointments, please book one by calling 12345678910 to schedule.";

  showOutput({
    role: "patient",
    access: "patient_record_view",
    records: [],
    message: "No appointments, please book one by calling 12345678910 to schedule.",
  });
}

async function handleResponse(response) {
  const data = await response.json();

  if (!response.ok || data.status === "error" || data.status === "failure") {
    throw new Error(data.message || "Request failed.");
  }

  return data;
}

async function checkEmail() {
  const email = document.getElementById("email-input").value.trim();

  if (!email) {
    showMessage("Please enter your email.", "error");
    return;
  }

  try {
    const response = await fetch(`${API_BASE}/check-email`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email }),
    });

    const data = await handleResponse(response);
    showOutput(data);

    selectedEmail = email;

    if (data.status === "existing_user") {
      selectedUsername = data.username;
      selectedRole = data.role;

      document.getElementById("login-email").value = email;
      document.getElementById("login-username").value = data.username;
      document.getElementById("login-role").value = data.role;

      showMessage("Account found. Enter your password to continue.", "success");
      showPanel(loginPanel);
      return;
    }

    document.getElementById("register-email").value = email;

    showMessage("No account found. Register to continue.", "info");
    showPanel(registerPanel);
  } catch (error) {
    showMessage(error.message, "error");
  }
}

async function registerUser() {
  const username = document.getElementById("register-username").value.trim();
  const role = document.getElementById("register-role").value;
  const password = document.getElementById("register-password").value;
  const email = document.getElementById("register-email").value.trim();

  if (!username || !role || !password || !email) {
    showMessage("Username, role, email, and password are required.", "error");
    return;
  }

  try {
    const registerResponse = await fetch(`${API_BASE}/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username,
        password,
        role,
        email,
      }),
    });

    const registerData = await handleResponse(registerResponse);
    showOutput(registerData);

    selectedEmail = email;
    selectedUsername = username;
    selectedRole = role;

    showMessage(
      "Registration complete. Sending your email verification code now.",
      "success"
    );

    await sendLoginRequest(username, password, role);
  } catch (error) {
    showMessage(error.message, "error");
  }
}

async function loginUser() {
  const username = document.getElementById("login-username").value.trim();
  const role = document.getElementById("login-role").value;
  const password = document.getElementById("login-password").value;

  if (!username || !role || !password) {
    showMessage("Username, role, and password are required.", "error");
    return;
  }

  await sendLoginRequest(username, password, role);
}

async function sendLoginRequest(username, password, role) {
  try {
    const response = await fetch(`${API_BASE}/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username,
        password,
        role,
      }),
    });

    const data = await handleResponse(response);
    showOutput(data);

    selectedUsername = data.username || username;
    selectedRole = data.role || role;

    document.getElementById("mfa-username").value = selectedUsername;

    showMessage(
      "Verification code sent through SendGrid. Check your email.",
      "success"
    );

    showPanel(mfaPanel);
  } catch (error) {
    showMessage(error.message, "error");
  }
}

async function verifyMfa() {
  const username = document.getElementById("mfa-username").value.trim();
  const code = document.getElementById("mfa-code").value.trim();

  if (!username || !code) {
    showMessage("Username and verification code are required.", "error");
    return;
  }

  try {
    const response = await fetch(`${API_BASE}/verify-mfa`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username,
        code,
      }),
    });

    const data = await handleResponse(response);
    showOutput(data);

    selectedUsername = data.username || username;
    selectedRole = data.role || selectedRole;

    updateSession(true, selectedUsername, selectedRole);
    assignRecordAccess(selectedUsername, selectedRole);

    showMessage("MFA verified. You are signed in.", "success");
    showPanel(protectedPanel);
  } catch (error) {
    showMessage(error.message, "error");
  }
}

async function getRecord() {
  const username = recordUsernameInput.value.trim();
  const recordId = recordIdInput.value.trim();

  if (selectedRole !== "provider") {
    showMessage("Only providers can retrieve Jane Doe's protected record.", "error");
    showOutput({
      status: "failure",
      message: "Only providers can retrieve Jane Doe's protected record.",
    });
    return;
  }

  if (!username || !recordId) {
    showMessage("Username and assigned record ID are required.", "error");
    return;
  }

  try {
    const response = await fetch(
      `${API_BASE}/records/${recordId}?username=${encodeURIComponent(username)}`
    );

    const data = await handleResponse(response);
    showOutput(data);

    showMessage("Jane Doe's protected asthma record retrieved.", "success");
  } catch (error) {
    showMessage(error.message, "error");
  }
}

async function getAuditLogs() {
  const username = auditUsernameInput.value.trim();

  if (selectedRole !== "admin") {
    showMessage("Only admins can view audit logs.", "error");
    showOutput({
      status: "failure",
      message: "Only admins can view audit logs.",
    });
    return;
  }

  if (!username) {
    showMessage("Admin username is required to view audit logs.", "error");
    return;
  }

  try {
    const response = await fetch(
      `${API_BASE}/admin/audit-text?username=${encodeURIComponent(username)}`
    );

    const data = await handleResponse(response);

    if (data.audit_text) {
      showTextOutput(data.audit_text);
    } else {
      showOutput(data);
    }

    showMessage("Audit logs retrieved.", "success");
  } catch (error) {
    showMessage(error.message, "error");
  }
}

function signOut() {
  selectedEmail = "";
  selectedUsername = "";
  selectedRole = "";

  updateSession(false);
  resetDashboards();

  showMessage("Signed out. Enter an email to begin again.", "success");
  showPanel(emailPanel);
}

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("email-continue-btn").addEventListener(
    "click",
    checkEmail
  );

  document.getElementById("register-btn").addEventListener(
    "click",
    registerUser
  );

  document.getElementById("login-btn").addEventListener("click", loginUser);
  document.getElementById("mfa-btn").addEventListener("click", verifyMfa);
  document.getElementById("record-btn").addEventListener("click", getRecord);
  document.getElementById("audit-btn").addEventListener("click", getAuditLogs);
  document.getElementById("signout-btn").addEventListener("click", signOut);

  updateSession(false);
  resetDashboards();
  showPanel(emailPanel);
});
