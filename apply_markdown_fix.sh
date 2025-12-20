#!/bin/bash
# Apply markdown formatting fix to all dashboard templates

cd /home/jkatz015/repos/hospitality_ai_agent/apps/dashboard/templates/dashboard

# CSS block to insert after .message-bubble closing brace
CSS_INSERT='
    /* Markdown formatting */
    .message-bubble strong {
      font-weight: 700;
    }

    .message-bubble ol,
    .message-bubble ul {
      margin: 10px 0;
      padding-left: 25px;
    }

    .message-bubble ol {
      list-style-type: decimal;
    }

    .message-bubble ul {
      list-style-type: disc;
    }

    .message-bubble li {
      margin: 6px 0;
      line-height: 1.6;
    }

    .message-bubble h3 {
      margin: 15px 0 8px 0;
      font-size: 1.05rem;
      font-weight: 700;
      border-bottom: 2px solid rgba(0,0,0,0.1);
      padding-bottom: 4px;
    }

    .message.assistant .message-bubble strong {
      color: #4338ca;
    }

    .message.user .message-bubble h3 {
      border-bottom-color: rgba(255,255,255,0.3);
    }
'

# Files to fix
FILES="beverage.html hr_solutions.html kpi_analysis.html recipes.html strategic_planning.html"

for file in $FILES; do
    if [ ! -f "$file" ]; then
        echo "⚠ $file not found, skipping"
        continue
    fi

    echo "Processing $file..."

    # Create backup
    cp "$file" "${file}.bak"

    # 1. Change line-height from 1.5 to 1.7 in .message-bubble
    sed -i 's/line-height: 1\.5;/line-height: 1.7;/g' "$file"

    # 2. Replace bubble.textContent with bubble.innerHTML
    sed -i 's/bubble\.textContent = content;/bubble.innerHTML = convertMarkdownToHTML(content);/g' "$file"

    echo "✓ $file updated"
done

echo "✅ All files processed. CSS and JS functions need to be added manually."
echo "Backup files created with .bak extension"
