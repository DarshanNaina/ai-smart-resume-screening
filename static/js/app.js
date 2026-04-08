document.addEventListener("DOMContentLoaded", function () {
  var roleInput = document.getElementById("id_role");
  var orgGroup = document.getElementById("org-name-group");
  if (roleInput && orgGroup) {
    var toggleOrgField = function () {
      var isHr = roleInput.value === "HR";
      orgGroup.style.display = isHr ? "block" : "none";
    };
    roleInput.addEventListener("change", toggleOrgField);
    toggleOrgField();
  }

  var resumeInput = document.getElementById("id_resume");
  var dropzone = document.getElementById("resume-dropzone");
  var info = document.getElementById("resume-file-info");
  if (resumeInput && dropzone) {
    var maxBytes = Number(resumeInput.dataset.maxBytes || 0);
    var updateInfo = function (file) {
      if (!info || !file) return;
      var sizeMb = (file.size / (1024 * 1024)).toFixed(2);
      info.textContent = "Selected: " + file.name + " (" + sizeMb + " MB)";
    };

    var validFile = function (file) {
      var ext = (file.name.split(".").pop() || "").toLowerCase();
      if (!["pdf", "docx"].includes(ext)) {
        alert("Only PDF or DOCX files are allowed.");
        return false;
      }
      if (maxBytes > 0 && file.size > maxBytes) {
        alert("File too large. Max allowed size exceeded.");
        return false;
      }
      return true;
    };

    resumeInput.addEventListener("change", function () {
      if (resumeInput.files && resumeInput.files[0]) {
        if (!validFile(resumeInput.files[0])) {
          resumeInput.value = "";
          return;
        }
        updateInfo(resumeInput.files[0]);
      }
    });

    ["dragenter", "dragover"].forEach(function (eventName) {
      dropzone.addEventListener(eventName, function (e) {
        e.preventDefault();
        dropzone.classList.add("dragover");
      });
    });
    ["dragleave", "drop"].forEach(function (eventName) {
      dropzone.addEventListener(eventName, function (e) {
        e.preventDefault();
        dropzone.classList.remove("dragover");
      });
    });

    dropzone.addEventListener("drop", function (e) {
      var file = e.dataTransfer.files[0];
      if (!file || !validFile(file)) return;
      var dt = new DataTransfer();
      dt.items.add(file);
      resumeInput.files = dt.files;
      updateInfo(file);
    });
  }
});
