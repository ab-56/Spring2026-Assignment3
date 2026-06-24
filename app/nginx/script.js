const API = "/api";

async function loadStudents() {
    const res = await fetch(`${API}/student`);
    const students = await res.json();

    document.getElementById("studentCount").innerText = students.length;

    const skillSelect = document.getElementById("studentSelect");
    const analysisSelect = document.getElementById("analysisStudent");

    skillSelect.innerHTML = "";
    analysisSelect.innerHTML = "";

    // Default select state placeholders handling
    const optDefault1 = document.createElement("option");
    optDefault1.value = "";
    optDefault1.text = "Select Student";
    optDefault1.disabled = true;
    optDefault1.selected = true;
    optDefault1.hidden = true;
    skillSelect.appendChild(optDefault1);

    const optDefault2 = document.createElement("option");
    optDefault2.value = "";
    optDefault2.text = "Select Student to Analyze";
    optDefault2.disabled = true;
    optDefault2.selected = true;
    optDefault2.hidden = true;
    analysisSelect.appendChild(optDefault2);

    students.forEach(student => {
        const option1 = document.createElement("option");
        option1.value = student.id;
        option1.text = `${student.name} (${student.career_goal})`;
        skillSelect.appendChild(option1);

        const option2 = document.createElement("option");
        option2.value = student.id;
        option2.text = `${student.name} (${student.career_goal})`;
        analysisSelect.appendChild(option2);
    });
}

async function addStudent() {
    const name = document.getElementById("name").value;
    const department = document.getElementById("department").value;
    const careerGoal = document.getElementById("careerGoal").value;
    const semester = document.getElementById("semester").value;
    const cgpa = document.getElementById("cgpa").value;

    if (!name) {
        alert("Student name required");
        return;
    }

    await fetch(`${API}/student`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            name,
            department,
            career_goal: careerGoal,
            semester,
            cgpa: parseFloat(cgpa || 0)
        })
    });

    // Reset fields after successful addition
    document.getElementById("name").value = "";
    document.getElementById("semester").value = "";
    document.getElementById("cgpa").value = "";
    document.getElementById("department").selectedIndex = 0;
    document.getElementById("careerGoal").selectedIndex = 0;

    await loadStudents();
    alert("Student Added Successfully");
}

async function addSkill() {
    const studentId = document.getElementById("studentSelect").value;
    const skill = document.getElementById("skillName").value;

    if (!studentId || !skill) {
        alert("Select student and skill");
        return;
    }

    await fetch(`${API}/skills`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            student_id: parseInt(studentId),
            skill_name: skill
        })
    });

    document.getElementById("skillName").selectedIndex = 0;
    alert("Skill Added Successfully");
}

async function loadReadiness() {
    const studentId = document.getElementById("analysisStudent").value;

    if (!studentId) {
        alert("Select Student");
        return;
    }

    /* STUDENT PROFILE */
    const studentRes = await fetch(`${API}/student/${studentId}`);
    const student = await studentRes.json();

    document.getElementById("currentCareer").innerText = student.career_goal;

    document.getElementById("studentProfile").innerHTML = `
        <p><b>Name:</b> ${student.name}</p>
        <p><b>Department:</b> ${student.department}</p>
        <p><b>Career Goal:</b> ${student.career_goal}</p>
        <p><b>Semester:</b> ${student.semester}</p>
        <p><b>CGPA:</b> ${student.cgpa}</p>
    `;

    /* SKILLS */
    const skillsRes = await fetch(`${API}/skills/${studentId}`);
    const skills = await skillsRes.json();

    let skillsHtml = "";
    skills.forEach(skill => {
        skillsHtml += `
            <span class="skill-badge">
                ${skill.skill_name}
            </span>
        `;
    });
    document.getElementById("studentSkills").innerHTML = skillsHtml || "<p style='color: #64748b; font-size: 0.9rem;'>No skills added yet.</p>";

    /* READINESS */
    const readinessRes = await fetch(`${API}/readiness/${studentId}`);
    const readiness = await readinessRes.json();

    document.getElementById("readinessScore").innerText = readiness.career_readiness_score + "%";
    let level = "Beginner";

    if (readiness.career_readiness_score >= 86) {   
    level = "Placement Ready";
}
    else if (readiness.career_readiness_score >= 61) {
    level = "Job Ready";
}
    else if (readiness.career_readiness_score >= 31) {
    level = "Intermediate";
}

document.getElementById("readinessLevel").innerText = level; 
    document.getElementById("progressBar").style.width = readiness.career_readiness_score + "%";

    let analysisHtml = `
        <h3>${readiness.student}</h3>
        <br>
        <h4>✅ Matched Skills</h4>
    `;

    if (readiness.matched_skills && readiness.matched_skills.length > 0) {
        readiness.matched_skills.forEach(skill => {
            analysisHtml += `<span class="skill-badge">${skill}</span>`;
        });
    } else {
        analysisHtml += `<span style="color: #64748b; font-size: 0.9rem; display:block; margin: 4px;">None</span>`;
    }

    analysisHtml += `
        <br><br>
        <h4>❌ Missing Skills</h4>
    `;

    if (readiness.missing_skills && readiness.missing_skills.length > 0) {
        readiness.missing_skills.forEach(skill => {
            analysisHtml += `<span class="missing-badge">${skill}</span>`;
        });
    } else {
        analysisHtml += `<span style="color: #64748b; font-size: 0.9rem; display:block; margin: 4px;">None</span>`;
    }

    analysisHtml += `
        <br><br>
        <h4>🛣️ Learning Roadmap</h4>
        <ul>
    `;

    readiness.roadmap.forEach(step => {
        analysisHtml += `<li>${step}</li>`;
    });

    analysisHtml += `</ul>`;
    document.getElementById("analysisResult").innerHTML = analysisHtml;

    /* CAREER MATCHES */
    const matchRes = await fetch(`${API}/career-match/${studentId}`);
    const matches = await matchRes.json();

    let matchHtml = "";
    matches.slice(0, 5).forEach(match => {
        // Structured using beautiful layout wrappers injected dynamically
        matchHtml += `
            <div class="career-match-item">
                <span>${match.career}</span>
                <strong>${match.score}%</strong>
            </div>
        `;
    });

    document.getElementById("careerMatches").innerHTML = matchHtml || "<p style='color: #64748b; font-size: 0.9rem;'>No tracks evaluated.</p>";
}

// Global Initialization
loadStudents();
