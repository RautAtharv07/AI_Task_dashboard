document.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("token");
  if (!token) {
    window.location.href = "index.html";
    return;
  }

  // DOM Elements
  const taskForm = document.getElementById("taskForm");
  const taskFormContainer = document.getElementById("taskFormContainer");
  const welcomeMsg = document.getElementById("welcomeMsg");
  const taskTableBody = document.getElementById("taskTableBody");
  const loadingIndicator = document.getElementById("loadingIndicator");
  const emptyState = document.getElementById("emptyState");
  const statusFilter = document.getElementById("statusFilter");
  const assignToSelect = document.getElementById("assignTo");
  const logoutBtn = document.getElementById("logoutBtn");

  let userRole = "employee"; // default
  let userEmail = "";
  let allTasks = [];
  let allEmployees = [];

  // Initialize the application
  init();

  async function init() {
    try {
      // Try to get user info, but continue even if it fails
      try {
        await getUserInfo();
      } catch (error) {
        console.log("User info endpoint not available, will determine role from dashboard data");
        // Set default values
        welcomeMsg.textContent = "Welcome to Task Dashboard";
      }
      
      await loadEmployees();
      await loadTasks();
      setupEventListeners();
    } catch (error) {
      console.error("Initialization failed:", error);
      handleAuthError();
    }
  }

  // Get user information - tries multiple endpoints
  async function getUserInfo() {
    try {
      console.log(`Trying endpoint: http://localhost:8000/me with token:`, token?.substring(0, 20) + "..."); 
      
      const response = await fetch("http://localhost:8000/me", {
        headers: { Authorization: `Bearer ${token}` }
      });

      console.log(`Response from /me:`, response.status);

      if (response.ok) {
        const user = await response.json();
        console.log("User data received:", user);
        
        // Handle user data from /me endpoint
        userRole = user.role || "employee";
        userEmail = user.email || "";
        const username = user.username || user.name || "User";
        
        // Update welcome message
        welcomeMsg.textContent = `Welcome, ${username} (${userRole.charAt(0).toUpperCase() + userRole.slice(1)})`;

        // Show appropriate UI based on role
        setupUIForRole();
        return; // Success
      } else {
        const errorText = await response.text();
        console.error("API Error Response:", errorText);
        throw new Error(`Failed to fetch user info: ${response.status} - ${errorText}`);
      }
    } catch (error) {
      console.error("User verification failed:", error);
      throw error; // Re-throw to be handled by init()
    }
  }

  // Setup UI based on user role
  function setupUIForRole() {
    if (userRole === "manager") {
      // Show task creation form for managers
      taskFormContainer.classList.remove("hidden");
      
      // Show all task filters for managers
      statusFilter.innerHTML = `
        <option value="">All Status</option>
        <option value="pending">Pending</option>
        <option value="in-progress">In Progress</option>
        <option value="completed">Completed</option>
      `;
    } else {
      // Employee view - only show their tasks
      taskFormContainer.classList.add("hidden");
      
      // Limited filters for employees
      statusFilter.innerHTML = `
        <option value="">My Tasks - All Status</option>
        <option value="pending">My Tasks - Pending</option>
        <option value="in-progress">My Tasks - In Progress</option>
        <option value="completed">My Tasks - Completed</option>
      `;
    }
  }

  // Load employees for task assignment (Manager only)
  async function loadEmployees() {
    if (userRole !== "manager") return;

    try {
      // Since there's no dedicated employees endpoint, we'll skip this for now
      // You might need to add a /users endpoint to your backend
      console.log("Employee loading skipped - no employees endpoint available");
      
      // For now, allow manual email entry
      if (assignToSelect) {
        assignToSelect.innerHTML = `
          <option value="">Select or enter employee email</option>
          <option value="employee1@example.com">employee1@example.com</option>
          <option value="employee2@example.com">employee2@example.com</option>
        `;
        
        // Make it editable
        assignToSelect.addEventListener('change', function() {
          if (this.value === '') {
            const email = prompt('Enter employee email:');
            if (email) {
              const option = document.createElement('option');
              option.value = email;
              option.textContent = email;
              option.selected = true;
              this.appendChild(option);
            }
          }
        });
      }
    } catch (error) {
      console.error("Failed to load employees:", error);
    }
  }

  // Populate employee select dropdown
  function populateEmployeeSelect() {
    if (!assignToSelect) return;

    assignToSelect.innerHTML = '<option value="">Select Employee to Assign</option>';
    allEmployees.forEach(employee => {
      const option = document.createElement("option");
      option.value = employee.email;
      option.textContent = `${employee.username} (${employee.email})`;
      assignToSelect.appendChild(option);
    });
  }

  // Load tasks and determine user role from response
  async function loadTasks() {
    showLoading(true);
    
    try {
      const response = await fetch("http://localhost:8000/tasks/", {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch tasks: ${response.status}`);
      }

      const data = await response.json();
      console.log("Tasks response:", data);

      // Handle response - should be array of tasks
      allTasks = Array.isArray(data) ? data : [];

      filterAndDisplayTasks();
      
    } catch (error) {
      console.error("Failed to load tasks:", error);
      
      // If it's an auth error, redirect to login
      if (error.message.includes("401") || error.message.includes("403")) {
        handleAuthError();
        return;
      }
      
      alert("Failed to load tasks. Please try again.");
    } finally {
      showLoading(false);
    }
  }

  // Filter and display tasks based on role and filters
  function filterAndDisplayTasks() {
    let filteredTasks = [...allTasks];

    // Filter by user role
    if (userRole === "employee") {
      filteredTasks = filteredTasks.filter(task => 
        task.assigned_to === userEmail || task.assigned_to === null
      );
    }

    // Filter by status
    const statusFilterValue = statusFilter.value;
    if (statusFilterValue) {
      filteredTasks = filteredTasks.filter(task => task.status === statusFilterValue);
    }

    displayTasks(filteredTasks);
  }

  // Display tasks in the table
  function displayTasks(tasks) {
    taskTableBody.innerHTML = "";

    if (tasks.length === 0) {
      emptyState.classList.remove("hidden");
      return;
    }

    emptyState.classList.add("hidden");

    tasks.forEach(task => {
      const tr = document.createElement("tr");
      tr.className = "hover:bg-gray-50";

      // Format deadline
      const deadline = task.deadline ? new Date(task.deadline).toLocaleDateString() : "—";
      
      // Determine status badge color
      const statusColor = getStatusColor(task.status);
      
      tr.innerHTML = `
        <td class="border px-4 py-2 font-medium">${escapeHtml(task.title)}</td>
        <td class="border px-4 py-2">${escapeHtml(task.description)}</td>
        <td class="border px-4 py-2">${deadline}</td>
        <td class="border px-4 py-2">${task.assigned_to || "Unassigned"}</td>
        <td class="border px-4 py-2">
          ${getStatusCell(task)}
        </td>
        <td class="border px-4 py-2">
          ${getActionCell(task)}
        </td>
      `;

      taskTableBody.appendChild(tr);
    });
  }

  // Get status cell content based on user role and task assignment
  function getStatusCell(task) {
    const statusColor = getStatusColor(task.status);
    
    // Allow employees to update status of their assigned tasks
    if (userRole === "employee" && task.assigned_to === userEmail) {
      return `
        <select class="px-2 py-1 rounded text-sm ${statusColor}" 
                onchange="updateTaskStatus(${task.id}, this.value)">
          <option value="pending" ${task.status === 'pending' ? 'selected' : ''}>Pending</option>
          <option value="in-progress" ${task.status === 'in-progress' ? 'selected' : ''}>In Progress</option>
          <option value="completed" ${task.status === 'completed' ? 'selected' : ''}>Completed</option>
        </select>
      `;
    }
    
    // For managers or unassigned tasks, show status badge
    return `<span class="px-2 py-1 rounded text-sm ${statusColor}">${task.status}</span>`;
  }

  // Get action cell content based on user role
  function getActionCell(task) {
    if (userRole === "manager") {
      return `
        <div class="flex gap-2">
          <button class="bg-blue-500 text-white px-2 py-1 rounded text-sm hover:bg-blue-600" 
                  onclick="editTask(${task.id})">Edit</button>
          <button class="bg-red-500 text-white px-2 py-1 rounded text-sm hover:bg-red-600" 
                  onclick="deleteTask(${task.id})">Delete</button>
        </div>
      `;
    }
    
    return "—";
  }

  // Get color class for status
  function getStatusColor(status) {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'in-progress':
        return 'bg-yellow-100 text-yellow-800';
      case 'pending':
      default:
        return 'bg-gray-100 text-gray-800';
    }
  }

  // Setup event listeners
  function setupEventListeners() {
    // Task form submission
    if (taskForm) {
      taskForm.addEventListener("submit", handleTaskSubmission);
    }

    // Status filter
    statusFilter.addEventListener("change", filterAndDisplayTasks);

    // Logout button
    logoutBtn.addEventListener("click", handleLogout);
  }

  // Handle task form submission
  async function handleTaskSubmission(e) {
    e.preventDefault();

    const title = document.getElementById("title").value.trim();
    const description = document.getElementById("description").value.trim();
    const deadline = document.getElementById("deadline").value;
    const assignedTo = assignToSelect.value;

    // Validation
    if (!title || !description) {
      alert("Please fill in title and description");
      return;
    }

    try {
      const taskData = { 
        title, 
        description, 
        deadline: deadline || null
      };

      // Create the task first
      const response = await fetch("http://localhost:8000/tasks/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(taskData)
      });

      if (response.ok) {
        const newTask = await response.json();
        
        // If assignment is specified, assign the task
        if (assignedTo && newTask.id) {
          try {
            // Note: You'll need to implement getting user_id from email
            // For now, we'll assume the backend can handle email-based assignment
            console.log(`Task created with ID: ${newTask.id}, assignment to ${assignedTo} needs to be implemented`);
          } catch (assignError) {
            console.error("Task created but assignment failed:", assignError);
          }
        }
        
        taskForm.reset();
        await loadTasks();
        alert("Task created successfully!");
      } else {
        const errorData = await response.json();
        alert(errorData.detail || "Task creation failed");
      }
    } catch (error) {
      console.error("Error creating task:", error);
      alert("Error creating task. Please try again.");
    }
  }

  // Update task status (for employees)
  window.updateTaskStatus = async function(taskId, newStatus) {
    try {
      const response = await fetch(`http://localhost:8000/tasks/${taskId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ status: newStatus })
      });

      if (response.ok) {
        await loadTasks();
      } else {
        alert("Failed to update task status");
      }
    } catch (error) {
      console.error("Error updating task status:", error);
      alert("Error updating task status. Please try again.");
    }
  };

  // Edit task (for managers)
  window.editTask = function(taskId) {
    // This could open a modal or redirect to an edit page
    // For now, let's just show an alert
    alert(`Edit task functionality for task ID: ${taskId} - To be implemented`);
  };

  // Delete task (Manager only)
  window.deleteTask = async function(taskId) {
    if (userRole !== "manager") {
      alert("Access denied. Only managers can delete tasks.");
      return;
    }

    if (!confirm("Are you sure you want to delete this task?")) return;

    try {
      const response = await fetch(`http://localhost:8000/tasks/${taskId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      if (response.ok) {
        await loadTasks();
        alert("Task deleted successfully!");
      } else {
        alert("Delete failed");
      }
    } catch (error) {
      console.error("Error deleting task:", error);
      alert("Error deleting task. Please try again.");
    }
  };

  // Handle logout
  function handleLogout() {
    if (confirm("Are you sure you want to logout?")) {
      localStorage.removeItem("token");
      window.location.href = "index.html";
    }
  }

  // Handle authentication errors
  function handleAuthError() {
    alert("Session expired. Please login again.");
    localStorage.removeItem("token");
    window.location.href = "index.html";
  }

  // Show/hide loading indicator
  function showLoading(show) {
    if (show) {
      loadingIndicator.classList.remove("hidden");
      emptyState.classList.add("hidden");
    } else {
      loadingIndicator.classList.add("hidden");
    }
  }

  // Escape HTML to prevent XSS
  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
});