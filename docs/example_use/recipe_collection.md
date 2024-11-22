# FlexTag Guide for Organizing Your Recipe Collection

FlexTag extends Markdown by providing a simple way to structure and organize documents. This guide will help you convert your recipes into a FlexTag document, allowing you to categorize, tag, and organize them efficiently.

## Core Concepts

A FlexTag document consists of three main parts:

1. **Document Settings** (`[[DOC]]`): Defines settings that affect the entire document.
2. **Document Metadata** (`[[META]]`): Contains information about the document itself.
3. **Sections** (`[[SEC]]`): Holds the actual content, organized into sections.

### 1. Document Settings (`[[DOC]]`)

Document settings appear at the very beginning and define global properties.

**Syntax:**
```markdown
[[DOC parameter1="value1" parameter2="value2" ...]]
```

**Example:**
```markdown
[[DOC fmt="text" enc="utf-8" lang="en"]]
```

- `fmt`: Format of the document (e.g., "text").
- `enc`: Encoding used (e.g., "utf-8").
- `lang`: Language of the document (e.g., "en" for English).

### 2. Document Metadata (`[[META]]`)

Metadata provides information about the document, similar to a book's cover details.

**Syntax:**
```markdown
[[META
  parameter1="value1"
  parameter2="value2"
  ...
]]
```

**Example:**
```markdown
[[META
  title="Family Recipe Collection"
  author="Your Name"
  version="1.0"
]]
```

- `title`: Title of the document.
- `author`: Author's name.
- `version`: Version number.

### 3. Sections (`[[SEC]]`)

Sections contain the main content. Each recipe will be a section with its own identifiers, tags, paths, and content.

**Syntax:**
```markdown
[[SEC:section_id #tag1 #tag2 .path1 .path2 parameter1="value1" parameter2="value2"]]
Content goes here.
[[/SEC]]
```

- `section_id`: Unique identifier for the section.
- `#tags`: Tags for categorization.
- `.paths`: Hierarchical paths for organization.
- `parameters`: Additional metadata for the section.

## Converting Recipes into FlexTag Format

Below are examples of how to convert recipes into FlexTag sections.

### Example 1: Spaghetti Bolognese

**FlexTag Section:**
```markdown
[[SEC:spaghetti_bolognese #italian #dinner .recipes.main_course .cuisine.italian .diet.gluten
  prep_time="15 minutes"
  cook_time="30 minutes"
  servings=4
]]
### Spaghetti Bolognese

**Ingredients:**
- 200g Spaghetti
- 250g Ground beef
- 400g Tomato sauce
- 1 Onion, chopped
- 2 cloves Garlic, minced
- Salt and pepper to taste

**Instructions:**
1. Cook the spaghetti according to package instructions.
2. In a separate pan, sauté onions and garlic until translucent.
3. Add ground beef and cook until browned.
4. Stir in tomato sauce, salt, and pepper. Simmer for 15 minutes.
5. Serve sauce over spaghetti.

[[/SEC]]
```

**Explanation:**

- **Section ID**: `spaghetti_bolognese` uniquely identifies the recipe.
- **Tags**: `#italian`, `#dinner` categorize the recipe.
- **Paths**:
  - `.recipes.main_course`: Categorizes under main courses.
  - `.cuisine.italian`: Associates with Italian cuisine.
  - `.diet.gluten`: Indicates it contains gluten.
- **Parameters**:
  - `prep_time`: Preparation time.
  - `cook_time`: Cooking time.
  - `servings`: Number of servings.

### Example 2: Quinoa Salad

**FlexTag Section:**
```markdown
[[SEC:quinoa_salad #vegan #healthy .recipes.salad .diet.vegan .ingredients.quinoa
  prep_time="10 minutes"
  cook_time="20 minutes"
  servings=2
]]
### Quinoa Salad

**Ingredients:**
- 1 cup Quinoa
- 1 cup Cherry tomatoes, halved
- 1 Cucumber, diced
- Juice of 1 Lemon
- 2 tbsp Olive oil
- Salt and pepper to taste

**Instructions:**
1. Rinse quinoa and cook according to package instructions. Let it cool.
2. In a bowl, combine quinoa, cherry tomatoes, and cucumber.
3. In a small bowl, whisk lemon juice, olive oil, salt, and pepper.
4. Pour dressing over the quinoa mixture and toss to combine.
5. Serve chilled or at room temperature.

[[/SEC]]
```

**Explanation:**

- **Section ID**: `quinoa_salad`
- **Tags**: `#vegan`, `#healthy`
- **Paths**:
  - `.recipes.salad`: Categorizes under salads.
  - `.diet.vegan`: Suitable for a vegan diet.
  - `.ingredients.quinoa`: Highlights quinoa as a key ingredient.
- **Parameters**:
  - `prep_time`, `cook_time`, `servings`

### Example 3: Chocolate Chip Cookies

**FlexTag Section:**
```markdown
[[SEC:chocolate_chip_cookies #dessert #baking .recipes.dessert .ingredients.chocolate .diet.vegetarian
  prep_time="15 minutes"
  cook_time="12 minutes"
  servings=24
]]
### Chocolate Chip Cookies

**Ingredients:**
- 1 cup Unsalted butter, softened
- 1 cup White sugar
- 1 cup Brown sugar
- 2 Eggs
- 2 tsp Vanilla extract
- 3 cups All-purpose flour
- 1 tsp Baking soda
- 2 cups Chocolate chips
- 1/2 tsp Salt

**Instructions:**
1. Preheat the oven to 350°F (175°C).
2. Cream together butter, white sugar, and brown sugar until smooth.
3. Beat in eggs one at a time, then stir in vanilla.
4. Dissolve baking soda in hot water and add to batter with salt.
5. Stir in flour and chocolate chips.
6. Drop large spoonfuls onto ungreased baking sheets.
7. Bake for about 10-12 minutes, or until edges are nicely browned.

[[/SEC]]
```

**Explanation:**

- **Section ID**: `chocolate_chip_cookies`
- **Tags**: `#dessert`, `#baking`
- **Paths**:
  - `.recipes.dessert`
  - `.ingredients.chocolate`
  - `.diet.vegetarian`
- **Parameters**:
  - `prep_time`, `cook_time`, `servings`

## Using Tags and Paths Effectively

### Tags (`#tag`)

- Use tags to categorize recipes based on characteristics like meal type or dietary preferences.
- Tags start with `#` and can include letters, numbers, and underscores.
- **Examples**: `#vegan`, `#gluten_free`, `#quick_meal`

### Paths (`.path`)

- Paths create a hierarchical organization, similar to folders and subfolders.
- Paths start with `.` and use dots to separate levels.
- A recipe can belong to multiple paths, allowing for flexible categorization.
- **Examples**: `.recipes.dinner`, `.cuisine.mexican`, `.diet.keto`

**Multiple Paths Example:**
```markdown
[[SEC:fish_tacos #seafood #mexican .recipes.main_course .cuisine.mexican .ingredients.fish]]
```
- This places "Fish Tacos" under multiple categories:
  - As a main course in recipes.
  - Under Mexican cuisine.
  - Highlighting fish as a key ingredient.

## Additional Parameters

- You can add custom parameters to provide more details about each recipe.
- Parameters are key-value pairs within the section header.
- **Examples**:
  - `difficulty="Easy"`
  - `calories=250`
  - `source="Grandma's Cookbook"`

**Example with Additional Parameters:**
```markdown
[[SEC:apple_pie #dessert #baking .recipes.dessert .ingredients.apple
  prep_time="30 minutes"
  cook_time="1 hour"
  servings=8
  difficulty="Medium"
  source="Family Recipe"
]]
```

## Best Practices for Organizing Recipes

- **Consistent Naming**: Use lowercase and underscores for section IDs, tags, and paths.
- **Meaningful Tags**: Choose tags that are broad enough to be useful but specific enough to be meaningful.
- **Hierarchical Paths**: Organize paths from general to specific (e.g., `.recipes.dessert.cakes`).
- **Use Multiple Paths**: Assign recipes to all relevant paths to enhance discoverability.
- **Include Parameters**: Add relevant parameters to provide additional context.

## Sample FlexTag Document Structure

**Full Example:**
```markdown
[[DOC fmt="text" enc="utf-8" lang="en"]]
[[META
  title="Family Recipe Collection"
  author="Your Name"
  version="1.0"
]]

[[SEC:spaghetti_bolognese #italian #dinner .recipes.main_course .cuisine.italian .diet.gluten
  prep_time="15 minutes"
  cook_time="30 minutes"
  servings=4
]]
... (recipe content) ...
[[/SEC]]

[[SEC:quinoa_salad #vegan #healthy .recipes.salad .diet.vegan .ingredients.quinoa
  prep_time="10 minutes"
  cook_time="20 minutes"
  servings=2
]]
... (recipe content) ...
[[/SEC]]

[[SEC:chocolate_chip_cookies #dessert #baking .recipes.dessert .ingredients.chocolate .diet.vegetarian
  prep_time="15 minutes"
  cook_time="12 minutes"
  servings=24
]]
... (recipe content) ...
[[/SEC]]
```

## How to Start Converting Your Recipes

1. **Gather Your Recipes**: Collect all the recipes you want to include.
2. **Identify Key Information**:
   - Ingredients
   - Instructions
   - Prep and cook times
   - Servings
3. **Determine Tags and Paths**:
   - Think about how you want to categorize each recipe.
   - Assign appropriate tags and paths.
4. **Create Section IDs**:
   - Use unique identifiers for each recipe, such as the recipe name in lowercase with underscores.
5. **Add Additional Parameters**:
   - Include any extra details that might be helpful.
6. **Assemble the FlexTag Sections**:
   - Follow the syntax provided to create each section.
7. **Compile the Document**:
   - Start with the `[[DOC]]` settings and `[[META]]` information.
   - Add all your recipe sections.

## Benefits of Using FlexTag for Recipes

- **Organization**: Easily categorize and find recipes.
- **Flexibility**: Assign multiple tags and paths to a single recipe.
- **Scalability**: Simple to add more recipes over time.
- **Searchability**: Enhanced ability to search for recipes based on various criteria.

## Conclusion

By converting your recipes into a FlexTag document, you create a structured and efficient way to manage your collection. The use of tags and paths allows for flexible categorization, making it easy to locate recipes based on cuisine, meal type, dietary requirements, and more.

Start organizing your recipes today using FlexTag, and enjoy the benefits of a well-structured recipe collection!
