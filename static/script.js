const apiBase = "/api/pokemon";
let pokemonCache = [];

const buildRow = (pokemon) => {
  const button = `<button class="select-button" data-id="${pokemon.id}">Edit</button>`;
  return `
    <tr>
      <td>${pokemon.id}</td>
      <td>${pokemon.name}</td>
      <td>${pokemon.type1 || ""}</td>
      <td>${pokemon.type2 || ""}</td>
      <td>${pokemon.hp}</td>
      <td>${pokemon.attack}</td>
      <td>${pokemon.defense}</td>
      <td>${pokemon.sp_atk}</td>
      <td>${pokemon.sp_def}</td>
      <td>${pokemon.speed}</td>
      <td>${pokemon.generation}</td>
      <td>${pokemon.legendary}</td>
      <td>${button}</td>
    </tr>
  `;
};

const renderTable = (items) => {
  const wrapper = document.getElementById("tableWrapper");
  if (!items.length) {
    wrapper.innerHTML = "<p>No records found.</p>";
    return;
  }

  wrapper.innerHTML = `
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Name</th>
          <th>Type 1</th>
          <th>Type 2</th>
          <th>HP</th>
          <th>Attack</th>
          <th>Defense</th>
          <th>Sp. Atk</th>
          <th>Sp. Def</th>
          <th>Speed</th>
          <th>Generation</th>
          <th>Legendary</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        ${items.map(buildRow).join("")}
      </tbody>
    </table>
  `;

  wrapper.querySelectorAll("button.select-button").forEach((button) => {
    button.addEventListener("click", () => selectPokemon(button.dataset.id));
  });
};

const loadPokemon = async () => {
  const response = await fetch(apiBase);
  pokemonCache = await response.json();
  renderTable(pokemonCache);
};

const selectPokemon = (id) => {
  const pokemon = pokemonCache.find((item) => item.id === Number(id));
  if (!pokemon) {
    return;
  }

  document.getElementById("pokemonId").value = pokemon.id;
  document.getElementById("dex_number").value = pokemon.dex_number;
  document.getElementById("name").value = pokemon.name;
  document.getElementById("type1").value = pokemon.type1 || "";
  document.getElementById("type2").value = pokemon.type2 || "";
  document.getElementById("hp").value = pokemon.hp;
  document.getElementById("attack").value = pokemon.attack;
  document.getElementById("defense").value = pokemon.defense;
  document.getElementById("sp_atk").value = pokemon.sp_atk;
  document.getElementById("sp_def").value = pokemon.sp_def;
  document.getElementById("speed").value = pokemon.speed;
  document.getElementById("generation").value = pokemon.generation;
  document.getElementById("legendary").value = pokemon.legendary.toString();
  updateSubmitLabel();
};

const clearForm = () => {
  document.getElementById("pokemonForm").reset();
  document.getElementById("pokemonId").value = "";
  updateSubmitLabel();
};

const getPayload = () => ({
  dex_number: Number(document.getElementById("dex_number").value),
  name: document.getElementById("name").value,
  type1: document.getElementById("type1").value || null,
  type2: document.getElementById("type2").value || null,
  hp: Number(document.getElementById("hp").value),
  attack: Number(document.getElementById("attack").value),
  defense: Number(document.getElementById("defense").value),
  sp_atk: Number(document.getElementById("sp_atk").value),
  sp_def: Number(document.getElementById("sp_def").value),
  speed: Number(document.getElementById("speed").value),
  generation: Number(document.getElementById("generation").value),
  legendary: document.getElementById("legendary").value === "true",
});

const updateSubmitLabel = () => {
  const id = document.getElementById("pokemonId").value;
  document.getElementById("submitButton").textContent = id ? "Save Changes" : "Add Pokemon";
};

const handleSave = async (event) => {
  event.preventDefault();
  const id = document.getElementById("pokemonId").value;
  const payload = getPayload();

  const response = await fetch(id ? `${apiBase}/${id}` : apiBase, {
    method: id ? "PATCH" : "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const error = await response.text();
    alert(`Failed to save: ${error}`);
    return;
  }

  if (id) {
    alert("Saved successfully.");
  } else {
    alert("Pokemon added successfully.");
  }

  await loadPokemon();
  clearForm();
};

const applyFilter = () => {
  const value = document.getElementById("searchInput").value.toLowerCase().trim();
  const filtered = pokemonCache.filter((item) => item.name.toLowerCase().includes(value));
  renderTable(filtered);
};

window.addEventListener("DOMContentLoaded", () => {
  document.getElementById("pokemonForm").addEventListener("submit", handleSave);
  document.getElementById("clearButton").addEventListener("click", clearForm);
  document.getElementById("searchInput").addEventListener("input", applyFilter);
  loadPokemon();
});
