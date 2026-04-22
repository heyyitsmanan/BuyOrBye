async function getSampleSets() {
  const response = await fetch("/api/samples");
  return response.json();
}

const linksInput = document.querySelector("#productLinks");
const statusMessage = document.querySelector("#statusMessage");
const metricsGrid = document.querySelector("#metricsGrid");
const recommendationsGrid = document.querySelector("#recommendationsGrid");
const comparisonGrid = document.querySelector("#comparisonGrid");
const priorityMode = document.querySelector("#priorityMode");
const categoryMode = document.querySelector("#categoryMode");

let sampleSets = {
  phones: [],
  headphones: [],
  laptops: [],
  "protein-oats": [],
};

document.querySelector("#loadSamples").addEventListener("click", async () => {
  await ensureSamples();
  linksInput.value = sampleSets.phones.join("\n");
  categoryMode.value = "auto";
  compareProducts();
});

document.querySelector("#compareNow").addEventListener("click", compareProducts);
document.querySelector("#resetComparison").addEventListener("click", resetComparison);

document.querySelectorAll(".pill").forEach((button) => {
  button.addEventListener("click", async () => {
    await ensureSamples();
    const key = button.dataset.sample;
    linksInput.value = sampleSets[key].join("\n");
    categoryMode.value = key;
    compareProducts();
  });
});

async function ensureSamples() {
  const hasSamples = Object.values(sampleSets).some((items) => items.length > 0);
  if (!hasSamples) {
    sampleSets = await getSampleSets();
  }
}

async function compareProducts() {
  const rawEntries = linksInput.value
    .split("\n")
    .map((entry) => entry.trim())
    .filter(Boolean);

  const response = await fetch("/api/compare", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      links: rawEntries,
      priority_mode: priorityMode.value,
      category_mode: categoryMode.value,
    }),
  });

  const payload = await response.json();
  statusMessage.textContent = payload.status_message;

  if (payload.error) {
    renderEmptyState(payload.status_message);
    return;
  }

  renderMetrics(payload.metrics);
  renderRecommendations(payload.recommendations, payload.products);
  renderProducts(payload.products);
}

function renderMetrics(metrics) {
  metricsGrid.innerHTML = "";
  const template = document.querySelector("#metricTemplate");

  metrics.forEach((metric) => {
    const node = template.content.cloneNode(true);
    node.querySelector(".metric-label").textContent = metric.label;
    node.querySelector(".metric-value").textContent = metric.value;
    node.querySelector(".metric-note").textContent = metric.note;
    metricsGrid.appendChild(node);
  });
}

function renderRecommendations(recommendations, products) {
  recommendationsGrid.innerHTML = "";
  const template = document.querySelector("#recommendationTemplate");
  const productMap = new Map(products.map((product) => [product.key, product]));

  recommendations.forEach((recommendation) => {
    const product = productMap.get(recommendation.product_key);
    const node = template.content.cloneNode(true);
    node.querySelector(".recommendation-label").textContent = recommendation.label;
    node.querySelector(".recommendation-score").textContent = recommendation.score;
    node.querySelector(".recommendation-score").classList.add(recommendation.tone_class);
    node.querySelector(".recommendation-title").textContent = product.name;
    node.querySelector(
      ".recommendation-subtitle"
    ).textContent = `${product.brand} | $${product.price} | ${product.rating}/5 rating`;
    node.querySelector(".recommendation-reason").textContent = recommendation.reason;
    recommendationsGrid.appendChild(node);
  });
}

function renderProducts(products) {
  comparisonGrid.innerHTML = "";
  const template = document.querySelector("#productTemplate");

  products.forEach((product) => {
    const node = template.content.cloneNode(true);
    node.querySelector(".product-brand").textContent = product.brand;
    node.querySelector(".product-name").textContent = product.name;
    node.querySelector(".price-badge").textContent = `$${product.price}`;
    node.querySelector(".price-score").textContent = `${product.price_score}/10`;
    node.querySelector(".quality-score").textContent = `${product.quality_score}/10`;
    node.querySelector(".value-score").textContent = `${product.value_score}/10`;
    node.querySelector(".product-summary").textContent = product.summary;

    const prosList = node.querySelector(".pro-list");
    product.pros.forEach((item) => {
      const listItem = document.createElement("li");
      listItem.textContent = item;
      prosList.appendChild(listItem);
    });

    const consList = node.querySelector(".con-list");
    product.cons.forEach((item) => {
      const listItem = document.createElement("li");
      listItem.textContent = item;
      consList.appendChild(listItem);
    });

    const specList = node.querySelector(".spec-list");
    product.specs.forEach((item) => {
      const tag = document.createElement("span");
      tag.className = "spec-item";
      tag.textContent = item;
      specList.appendChild(tag);
    });

    comparisonGrid.appendChild(node);
  });
}

function renderEmptyState(message) {
  metricsGrid.innerHTML = "";
  recommendationsGrid.innerHTML = "";
  comparisonGrid.innerHTML = `
    <article class="card">
      <p class="section-kicker">Ready when you are</p>
      <h2>Build the first comparison</h2>
      <p class="metric-note">${message}</p>
    </article>
  `;
}

function resetComparison() {
  linksInput.value = "";
  priorityMode.value = "balanced";
  categoryMode.value = "auto";
  statusMessage.textContent = "Comparison reset. Add product links or try a sample set.";
  renderEmptyState(
    "Paste product links or use a sample set to see price comparison, pros and cons, and recommendation logic."
  );
}

renderEmptyState(
  "Paste product links or use a sample set to see price comparison, pros and cons, and recommendation logic."
);
