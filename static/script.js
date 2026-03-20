function previewImage(input, targetId) {
  const file = input.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = () => {
    document.getElementById(targetId).src = reader.result;
  };
  reader.readAsDataURL(file);
}

async function analyze(username) {
  const form = document.getElementById("analyzeForm");
  const data = new FormData(form);

  document.getElementById("output").innerText = "Analyzing...";

  const res = await fetch(`/home/${username}`, {
    method: "POST",
    body: data
  });

  const json = await res.json();
  document.getElementById("output").innerText =
    JSON.stringify(json, null, 2);
}
