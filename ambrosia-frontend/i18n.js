const TRANSLATIONS = {
  uk: {
    page_title: "RagweedGrid UA",
    brand: "🌿 RagweedGrid UA",
    nav_home: "Головна",
    nav_problem: "Проблема",
    nav_map: "Карта",
    nav_methodology: "Методологія",
    hero_title: "Карта придатності територій для амброзії в Україні",
    hero_subtitle: "Модель машинного навчання оцінює, наскільки клімат і земля в місцевості схожі на ті, де амброзію полинолисту вже фіксували. Це допомагає побачити, де варто уважніше стежити за її появою.",
    hero_cta: "Переглянути карту",
    problem_title: "Чому це важливо",
    problem_health_title: "Здоров’я людей",
    problem_health_text: "Пилок амброзії належить до сильних алергенів і може спричиняти сенсибілізацію навіть у людей, які раніше не мали алергії. Особливо помітним його вплив стає у сезон цвітіння у вітряну погоду.",
    problem_eco_title: "Екологічна шкода",
    problem_eco_text: "Амброзія заселяє переважно порушені землі, але може проникати й у природні оселища та конкурувати з місцевими видами рослин. Вплив на природні екосистеми вивчений менше, ніж на здоров’я людей і сільське господарство.",
    problem_agri_title: "Сільське господарство",
    problem_agri_text: "Як бур’ян, амброзія знижує врожайність сільськогосподарських культур і потребує додаткових витрат на боротьбу з нею.",
    map_title: "Інтерактивна карта",
    map_subtitle: "Кожна точка є точкою регулярної сітки 0,2°, для якої модель розрахувала відносний індекс придатності (клімат 2015–2024 та частки ріллі й забудови). Індекс показує схожість умов на місця зі знахідками, а не те, чи росте амброзія в цій точці. Кольори відносні, докладніше про них у розділі «Методологія».",
    legend_low: "Нижча",
    legend_medium: "Середня",
    legend_high: "Вища",
    search_title: "Перевірити конкретне місце",
    search_subtitle: "Введіть назву міста чи села або просто клікніть по карті, і модель розрахує індекс для цієї точки.",
    place_placeholder: "Місто або село, напр. Львів",
    lat_placeholder: "Широта, напр. 49.84",
    lon_placeholder: "Довгота, напр. 24.03",
    place_button: "Знайти",
    manual_summary: "Ввести координати вручну",
    search_button: "Розрахувати",
    explain_button: "🤖 Пояснити простими словами",
    method_title: "Методологія",
    method_1: "Дані про спостереження амброзії взято з GBIF (Global Biodiversity Information Facility): лише спостереження людей за 2015–2024 роки, очищені за датою, координатами та точністю геолокації (до 5 км). Це 3096 записів, згрупованих у 782 комірки сітки 0,1° (781 комірка з повними ознаками використана для навчання).",
    method_2: "Клімат (температура, опади, вологість за сезон квітень–жовтень, 2015–2024) отримано з Open-Meteo Historical Weather API. Частки ріллі та забудови взято з ESA WorldCover 2020 і усереднено по комірках 0,1° (≈ 7–11 км).",
    method_3: "Достовірних даних про відсутність амброзії немає, тому для порівняння використано фонові комірки: місця, де спостерігали інші рослини (GBIF), з імовірністю, пропорційною інтенсивності спостережень. Це частково враховує те, що люди частіше фіксують спостереження в містах.",
    method_4: "Модель: Random Forest (500 дерев). Перевірка на регіонах, яких модель не бачила (просторова крос-валідація, блоки 2°×2°): AUC-ROC ≈ 0,68.",
    method_5: "Для довільної точки сервер намагається отримати клімат у реальному часі (якщо це не вдається, бере клімат найближчої точки сітки), знаходить частки землі, розраховує індекс і порівнює його з розподілом по території України. Категорії відносні: нижні 50% точок карти зелені, наступні 30% помаранчеві, верхні 20% червоні.",
    method_6: "Поради у поясненні генерує мовна модель на основі результату. Вони орієнтовані на загальні рекомендації Держпродспоживслужби України щодо боротьби з амброзією полинолистою (обстеження територій і знищення рослин до початку цвітіння), мають загальний характер і не замінюють рекомендацій місцевих служб.",
    method_limitation: "Обмеження: це відносний індекс придатності, а не ймовірність наявності амброзії. Точність помірна (AUC-ROC ≈ 0,66–0,68). Як «відсутність» у навчальних даних використано лише фонові точки. Оцінка надійніша там, де багато спостерігачів, а у великих містах вища частка забудови може давати вищий індекс схожості умов. Земельний покрив взято зі знімка 2020 року; дороги та динаміка не враховані. Якщо живі кліматичні дані тимчасово недоступні, для точки використовується клімат найближчої точки сітки.",
    footer_html: 'RagweedGrid UA: оцінка придатності територій для амброзії полинолистої в Україні. Дані: GBIF (DOI: <a href="https://doi.org/10.15468/dl.dndrth" target="_blank" rel="noopener">знахідки</a> · <a href="https://doi.org/10.15468/dl.qsftj6" target="_blank" rel="noopener">фон</a>) · <a href="https://open-meteo.com" target="_blank" rel="noopener">Open-Meteo</a> · <a href="https://esa-worldcover.org" target="_blank" rel="noopener">ESA WorldCover 2020</a> · © OpenStreetMap contributors',
    result_index: "Індекс придатності",
    result_percentile: "Вище, ніж на {n}% території України",
    result_land: "Земельний покрив навколо",
    land_cropland: "рілля",
    land_built: "забудова",
    result_note: "Відносний індекс: наскільки умови схожі на місця, де фіксували амброзію. Це не ймовірність її наявності.",
    climate_grid_note: "Клімат взято з сусідньої комірки карти: сервіс погодних даних тимчасово недоступний.",
    result_place: "Місце",
    result_point: "Точка на карті",
    result_category_low: "нижча",
    result_category_medium: "середня",
    result_category_high: "вища",
    place_pick: "Знайдено кілька місць, оберіть потрібне:",
    place_not_found: "Місце не знайдено. Спробуйте іншу назву.",
    place_error: "Не вдалось виконати пошук. Спробуйте ще раз.",
    place_empty: "Введіть назву місця.",
    place_region_hint: "Пошук за областями не підтримується. Введіть назву міста чи села або клікніть по карті.",
    error_fill_fields: "Будь ласка, введіть коректні координати.",
    error_generic: "Сталася помилка. Спробуйте ще раз.",
    error_no_land: "Для цієї точки немає даних про земельний покрив (це може бути море або місце поза територією, яку покриває модель).",
    error_climate: "Не вдалося отримати кліматичні дані для цієї точки. Спробуйте ще раз пізніше.",
    error_outside_ukraine: "Ця точка поза Україною. Модель навчена на даних України, тому для таких місць результат не розраховується.",
    waking: "Сервер прокидається після простою, це може тривати до хвилини. Будь ласка, зачекайте.",
    explain_loading: "Формуємо пояснення...",
    waking_explain: "Сервер ШІ зараз перевантажений, тому відповідь може йти до хвилини. Будь ласка, зачекайте.",
    explain_fallback_note: "Через велике навантаження на безкоштовний сервер ШІ показано автоматичне пояснення за шаблоном.",
    explain_ai_note: "Пояснення створено ШІ, тож може містити помилки. Будь ласка, перевіряйте рекомендації.",
    result_climate: "Клімат (квітень–жовтень): {t} °C, опади {p} мм/день, вологість {h}%",
    loading: "Розраховуємо...",
    searching: "Шукаємо..."
  },
  en: {
    page_title: "RagweedGrid UA",
    brand: "🌿 RagweedGrid UA",
    nav_home: "Home",
    nav_problem: "Problem",
    nav_map: "Map",
    nav_methodology: "Methodology",
    hero_title: "Ragweed Suitability Map for Ukraine",
    hero_subtitle: "A machine learning model estimates how similar the climate and land in an area are to places where common ragweed (Ambrosia artemisiifolia) has already been recorded. It helps show where it is worth watching more closely for its appearance.",
    hero_cta: "View the map",
    problem_title: "Why it matters",
    problem_health_title: "Human health",
    problem_health_text: "Ragweed pollen is a strong allergen and can cause sensitisation even in people who previously had no allergies. Its effects become especially noticeable during the flowering season in windy weather.",
    problem_eco_title: "Ecological damage",
    problem_eco_text: "Ragweed colonises mainly disturbed land, but it can also invade natural habitats and compete with native plant species. Its impact on natural ecosystems is less studied than its effects on human health and agriculture.",
    problem_agri_title: "Agriculture",
    problem_agri_text: "As a weed, ragweed reduces crop yields and requires additional costs to control.",
    map_title: "Interactive map",
    map_subtitle: "Each point is a point of a regular 0.2° grid for which the model computed a relative suitability index (2015–2024 climate plus the share of cropland and built-up land). The index shows how similar conditions are to places with records, not whether ragweed grows at that point. Colours are relative; see the Methodology section for details.",
    legend_low: "Lower",
    legend_medium: "Medium",
    legend_high: "Higher",
    search_title: "Check a specific location",
    search_subtitle: "Type a city or village name, or just click on the map, and the model will compute the index for that point.",
    place_placeholder: "City or village, e.g. Lviv",
    lat_placeholder: "Latitude, e.g. 49.84",
    lon_placeholder: "Longitude, e.g. 24.03",
    place_button: "Search",
    manual_summary: "Enter coordinates manually",
    search_button: "Calculate",
    explain_button: "🤖 Explain in plain words",
    method_title: "Methodology",
    method_1: "Ragweed occurrence data comes from GBIF (Global Biodiversity Information Facility): human observations only, 2015–2024, cleaned by date, coordinates and geolocation precision (up to 5 km). That is 3,096 records grouped into 782 cells of a 0.1° grid (781 cells with complete features used for training).",
    method_2: "Climate (temperature, precipitation, humidity for the April–October season, 2015–2024) comes from the Open-Meteo Historical Weather API. Cropland and built-up shares come from ESA WorldCover 2020, averaged per 0.1° cell (≈ 7–11 km).",
    method_3: "True absence of ragweed is unknown, so background cells are used for comparison: places where other plants were observed (GBIF), sampled in proportion to sampling intensity. This partially accounts for the fact that people record observations more often in cities.",
    method_4: "The model is a Random Forest (500 trees). Tested on regions it has not seen (spatial cross-validation, 2°×2° blocks): AUC-ROC ≈ 0.68.",
    method_5: "For any point the server tries to fetch live climate (if that fails, it uses the climate of the nearest grid point), looks up the land shares, computes the index and compares it with the distribution across Ukraine. Categories are relative: the lowest 50% of map points are green, the next 30% orange and the top 20% red.",
    method_6: "The tips in the explanation are generated by a language model from the result. They are guided by general recommendations of the State Service of Ukraine on Food Safety and Consumer Protection on controlling common ragweed (surveying territories and destroying plants before flowering), are general in nature and do not replace the guidance of local services.",
    method_limitation: "Limitations: this is a relative suitability index, not a probability that ragweed is present. Accuracy is moderate (AUC-ROC ≈ 0.66–0.68). Only background points were used as “absences” in the training data. Estimates are more reliable where many observers are active, and a higher built-up share in large cities can yield a higher index of condition similarity. Land cover is a 2020 snapshot; roads and change over time are not included. If live climate data is temporarily unavailable, the climate of the nearest grid point is used.",
    footer_html: 'RagweedGrid UA: assessment of territory suitability for common ragweed in Ukraine. Data: GBIF (DOI: <a href="https://doi.org/10.15468/dl.dndrth" target="_blank" rel="noopener">occurrences</a> · <a href="https://doi.org/10.15468/dl.qsftj6" target="_blank" rel="noopener">background</a>) · <a href="https://open-meteo.com" target="_blank" rel="noopener">Open-Meteo</a> · <a href="https://esa-worldcover.org" target="_blank" rel="noopener">ESA WorldCover 2020</a> · © OpenStreetMap contributors',
    result_index: "Suitability index",
    result_percentile: "Higher than {n}% of Ukraine’s territory",
    result_land: "Land cover nearby",
    land_cropland: "cropland",
    land_built: "built-up",
    result_note: "Relative index: how similar conditions are to places where ragweed has been recorded. It is not a probability that it is present.",
    climate_grid_note: "Climate is taken from a neighbouring map cell because the weather data service is temporarily unavailable.",
    result_place: "Place",
    result_point: "Point on the map",
    result_category_low: "lower",
    result_category_medium: "medium",
    result_category_high: "higher",
    place_pick: "Several places found, pick the right one:",
    place_not_found: "Place not found. Try another name.",
    place_error: "Search failed. Please try again.",
    place_empty: "Please enter a place name.",
    place_region_hint: "Searching by region is not supported. Enter a city or village name, or click on the map.",
    error_fill_fields: "Please enter valid coordinates.",
    error_generic: "Something went wrong. Please try again.",
    error_no_land: "There is no land cover data for this point (it may be sea or a place outside the area covered by the model).",
    error_climate: "Could not get climate data for this point. Please try again later.",
    error_outside_ukraine: "This point is outside Ukraine. The model was trained on Ukrainian data, so no result is calculated for such places.",
    waking: "The server is waking up after inactivity. This can take up to a minute, please wait.",
    explain_loading: "Preparing the explanation...",
    waking_explain: "The AI server is currently overloaded, so the answer may take up to a minute. Please wait.",
    explain_fallback_note: "Due to high load on the free AI server, an automatic template explanation is shown.",
    explain_ai_note: "This explanation was created by AI, so it may contain mistakes. Please verify the recommendations.",
    result_climate: "Climate (April–October): {t} °C, precipitation {p} mm/day, humidity {h}%",
    loading: "Calculating...",
    searching: "Searching..."
  }
};

let currentLang = localStorage.getItem("lang") || "uk";

function applyTranslations() {
  const dict = TRANSLATIONS[currentLang];
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.getAttribute("data-i18n");
    if (dict[key]) el.textContent = dict[key];
  });
  document.querySelectorAll("[data-i18n-html]").forEach(el => {
    const key = el.getAttribute("data-i18n-html");
    if (dict[key]) el.innerHTML = dict[key];
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
    const key = el.getAttribute("data-i18n-placeholder");
    if (dict[key]) el.placeholder = dict[key];
  });
  if (dict.page_title) document.title = dict.page_title;
  document.documentElement.lang = currentLang;
}

function toggleLang() {
  currentLang = currentLang === "uk" ? "en" : "uk";
  localStorage.setItem("lang", currentLang);
  applyTranslations();
}

document.addEventListener("DOMContentLoaded", () => {
  applyTranslations();
  document.getElementById("lang-toggle").addEventListener("click", toggleLang);
});
