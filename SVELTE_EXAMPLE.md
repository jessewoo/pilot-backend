# Using Wagtail API with Svelte Frontend

## API Endpoints

### Get Homepage
```
GET http://localhost:8000/api/v2/pages/?type=home.HomePage&fields=*
```

Or by slug:
```
GET http://localhost:8000/api/v2/page-by-slug/?slug=home
```

## Svelte Component Example

### HomePage.svelte
```svelte
<script>
  import { onMount } from 'svelte';

  let pageData = null;
  let loading = true;

  onMount(async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v2/page-by-slug/?slug=home');
      const data = await response.json();
      pageData = data;
      loading = false;
    } catch (error) {
      console.error('Error fetching homepage:', error);
      loading = false;
    }
  });
</script>

{#if loading}
  <div>Loading...</div>
{:else if pageData}

  <!-- Hero Section -->
  {#if pageData.hero_title}
    <section class="hero">
      {#if pageData.hero_image}
        <img src={pageData.hero_image} alt={pageData.hero_title} />
      {/if}
      <h1>{pageData.hero_title}</h1>
      {#if pageData.hero_subtitle}
        <p>{pageData.hero_subtitle}</p>
      {/if}
      {#if pageData.hero_cta_text && pageData.hero_cta_link}
        <a href={pageData.hero_cta_link} class="cta-button">
          {pageData.hero_cta_text}
        </a>
      {/if}
    </section>
  {/if}

  <!-- About Section -->
  {#if pageData.about_title}
    <section class="about">
      <h2>{pageData.about_title}</h2>
      <div>{@html pageData.about_content}</div>
    </section>
  {/if}

  <!-- Dynamic Content Sections -->
  {#if pageData.content_sections}
    {#each JSON.parse(pageData.content_sections) as section}

      <!-- Stats Section -->
      {#if section.type === 'stats_section'}
        <section class="stats">
          {#if section.value.title}
            <h2>{section.value.title}</h2>
          {/if}
          <div class="stats-grid">
            {#each section.value.stats as stat}
              <div class="stat-box">
                <div class="stat-number">{stat.number}</div>
                <div class="stat-label">{stat.label}</div>
                {#if stat.description}
                  <p class="stat-description">{stat.description}</p>
                {/if}
              </div>
            {/each}
          </div>
        </section>
      {/if}

      <!-- Links Section -->
      {#if section.type === 'links_section'}
        <section class="links">
          {#if section.value.title}
            <h2>{section.value.title}</h2>
          {/if}
          <div class="links-grid">
            {#each section.value.links as link}
              <a href={link.url} class="link-card">
                {#if link.icon}
                  <span class="icon">{link.icon}</span>
                {/if}
                <h3>{link.title}</h3>
                {#if link.description}
                  <p>{link.description}</p>
                {/if}
              </a>
            {/each}
          </div>
        </section>
      {/if}

      <!-- Content Boxes -->
      {#if section.type === 'content_boxes'}
        <section class="content-boxes">
          {#if section.value.title}
            <h2>{section.value.title}</h2>
          {/if}
          <div class="boxes-grid">
            {#each section.value.boxes as box}
              <div class="content-box">
                {#if box.image}
                  <img src={box.image} alt={box.title} />
                {/if}
                <h3>{box.title}</h3>
                <div>{@html box.content}</div>
                {#if box.link_url && box.link_text}
                  <a href={box.link_url}>{box.link_text}</a>
                {/if}
              </div>
            {/each}
          </div>
        </section>
      {/if}

      <!-- Project Highlights -->
      {#if section.type === 'project_highlights'}
        <section class="projects">
          <h2>{section.value.section_title}</h2>
          <div class="projects-grid">
            {#each section.value.projects as project}
              <div class="project-card">
                {#if project.image}
                  <img src={project.image} alt={project.title} />
                {/if}
                <h3>{project.title}</h3>
                <p>{project.description}</p>
                {#if project.tags && project.tags.length > 0}
                  <div class="tags">
                    {#each project.tags as tag}
                      <span class="tag">{tag}</span>
                    {/each}
                  </div>
                {/if}
                {#if project.link_url}
                  <a href={project.link_url}>{project.link_text}</a>
                {/if}
              </div>
            {/each}
          </div>
        </section>
      {/if}

      <!-- News Section -->
      {#if section.type === 'news_section'}
        <section class="news">
          <h2>{section.value.section_title}</h2>
          <div class="news-grid">
            {#each section.value.news_items as news}
              <article class="news-item">
                {#if news.image}
                  <img src={news.image} alt={news.title} />
                {/if}
                <div class="news-meta">
                  <time>{new Date(news.date).toLocaleDateString()}</time>
                  {#if news.category}
                    <span class="category">{news.category}</span>
                  {/if}
                </div>
                <h3>{news.title}</h3>
                <p>{news.summary}</p>
                {#if news.link_url}
                  <a href={news.link_url}>Read more</a>
                {/if}
              </article>
            {/each}
          </div>
        </section>
      {/if}

      <!-- Custom HTML -->
      {#if section.type === 'custom_html'}
        <section class="custom-html">
          {@html section.value}
        </section>
      {/if}

    {/each}
  {/if}

{/if}

<style>
  .hero {
    text-align: center;
    padding: 4rem 2rem;
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 2rem;
    margin: 2rem 0;
  }

  .stat-box {
    text-align: center;
    padding: 2rem;
    background: #f5f5f5;
    border-radius: 8px;
  }

  .stat-number {
    font-size: 2.5rem;
    font-weight: bold;
    color: #2563eb;
  }

  .links-grid, .boxes-grid, .projects-grid, .news-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 2rem;
    margin: 2rem 0;
  }

  .link-card, .content-box, .project-card, .news-item {
    padding: 1.5rem;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    transition: box-shadow 0.3s;
  }

  .link-card:hover, .content-box:hover, .project-card:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  }

  .tags {
    display: flex;
    gap: 0.5rem;
    margin: 1rem 0;
    flex-wrap: wrap;
  }

  .tag {
    background: #dbeafe;
    color: #1e40af;
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    font-size: 0.875rem;
  }
</style>
```

## API Response Structure

The API will return JSON like this:

```json
{
  "id": 3,
  "title": "Home",
  "slug": "home",
  "hero_title": "Welcome to NAIRR Pilot",
  "hero_subtitle": "National AI Research Resource",
  "hero_image": "http://localhost:8000/media/images/hero.jpg",
  "hero_cta_text": "Get Started",
  "hero_cta_link": "https://example.com/signup",
  "about_title": "About NAIRR",
  "about_content": "<p>Rich text content here...</p>",
  "content_sections": "[
    {
      \"type\": \"stats_section\",
      \"value\": {
        \"title\": \"Our Impact\",
        \"stats\": [
          {\"number\": \"500+\", \"label\": \"Users\"},
          {\"number\": \"$10M\", \"label\": \"Funding\"}
        ]
      }
    },
    {
      \"type\": \"project_highlights\",
      \"value\": {
        \"section_title\": \"Featured Projects\",
        \"projects\": [...]
      }
    }
  ]"
}
```

## Steps to Use

1. **Run migrations** to update HomePage model:
   ```bash
   python manage.py makemigrations home
   python manage.py migrate home
   ```

2. **Edit your homepage** in Wagtail admin at `http://localhost:8000/admin/`

3. **Fetch data in Svelte** using the example code above

4. The `content_sections` field is a JSON string, so parse it: `JSON.parse(pageData.content_sections)`

5. Loop through sections and render based on `type` field

## Alternative: Create Svelte Components

```javascript
// components/StatsSection.svelte
// components/LinksSection.svelte
// components/ProjectHighlights.svelte
// components/NewsSection.svelte
```

Then import and use them in your main HomePage component based on section type.
