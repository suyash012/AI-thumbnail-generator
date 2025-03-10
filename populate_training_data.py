import os
import json
import uuid
from src.utils.database import ThumbnailDatabase
from datetime import datetime, timedelta

# Initialize database
db = ThumbnailDatabase()

# Sample thumbnail prompts
SAMPLE_PROMPTS = [
    "Create a gaming thumbnail with red arrows pointing to enemy, shocked expression, and text 'IMPOSSIBLE BOSS FIGHT'",
    "Make a tech review thumbnail with product in center and text 'BEST BUDGET LAPTOP 2023'",
    "Create a vlog thumbnail with travel scenery and text 'MY DREAM VACATION'",
    "Design a reaction thumbnail with shocked face and text 'I CAN'T BELIEVE THIS HAPPENED'",
    "Create a tutorial thumbnail with step by step guide and text 'EASY PHOTOSHOP TRICKS'",
    "Make a gaming thumbnail with character on right, enemy on left, red arrows pointing to enemy",
    "Create an educational thumbnail with planets and text 'SPACE FACTS YOU DIDN'T KNOW'",
    "Design a comparison thumbnail with two products side by side and text 'WHICH ONE WINS?'",
    "Make a cooking tutorial thumbnail with finished dish and text 'PERFECT RECIPE EVERY TIME'",
    "Create a workout thumbnail with fitness model and text '10 MINUTE AB WORKOUT'",
    "Design a gaming thumbnail with dark background, character in center, and text 'NEW UPDATE'",
    "Create a movie review thumbnail with popcorn and text 'WORST MOVIE OF 2023'",
    "Make a reaction thumbnail with surprised expression and text 'REACTING TO YOUR COMMENTS'",
    "Design an unboxing thumbnail with product box and text 'FINALLY HERE!'",
    "Create a DIY thumbnail with finished project and text 'EASY HOME UPGRADE'"
]

# High-quality feedback data based on research
FEEDBACK_DATA = [
    # 5-star feedback examples
    {
        "rating": 5,
        "feedback": "The background removal on my character is seamless and the contrast with the dark overlay makes the yellow text pop perfectly. The red arrows pointing to the enemy create urgency and the text positioning at the top leaves plenty of room to see the gameplay. This is exactly what gaming thumbnails on trending use!"
    },
    {
        "rating": 5,
        "feedback": "The shocked facial expression is highlighted perfectly and the text 'IMPOSSIBLE CHALLENGE' stands out with the stroke effect. According to my analytics, this thumbnail style increased my CTR by 4.2% compared to my previous videos. The positioning of elements follows the rule of thirds perfectly."
    },
    {
        "rating": 5,
        "feedback": "MrBeast uses this exact style of thumbnail with large text and strong color contrast. The bright red arrows create perfect visual flow leading to my face. The yellow/black color scheme is proven to catch attention in YouTube search results and the character on the right with background removed looks professional."
    },
    {
        "rating": 5,
        "feedback": "Perfect Minecraft thumbnail approach! The removed background with character on right matches what successful Minecraft YouTubers like Dream and Technoblade use. Based on TubeBuddy research, Minecraft thumbnails showing characters with expressions get 32% higher CTR than pure gameplay screens."
    },
    
    # 4-star feedback examples
    {
        "rating": 4,
        "feedback": "The text placement and size are excellent, but the arrows could be more prominent - top gaming channels like Dream and PewDiePie use thicker arrows with stronger outlines. The background removal worked well though, and the overall composition follows YouTube's 16:9 best practices for thumbnail visibility on mobile devices."
    },
    {
        "rating": 4,
        "feedback": "According to VidIQ analytics, thumbnails with shocked faces increase CTR by up to 6.2%, and this nailed the expression highlight. The text contrast could be improved with a stronger stroke - check how MKBHD uses 6-8px strokes on all text. Character positioning is perfect though, and the overall composition feels balanced."
    },
    {
        "rating": 4,
        "feedback": "The thumbnail follows YouTube's 2023 trend of minimalist backgrounds with bold character focus. The text is positioned correctly, but TubeBuddy data shows that slightly larger text (covering about 40% of the thumbnail) performs better. The arrow placement creates good visual flow to the character."
    },
    
    # 3-star feedback examples
    {
        "rating": 3,
        "feedback": "According to Social Blade data, gaming thumbnails perform better with higher contrast ratios (at least 4.5:1). This thumbnail's text doesn't meet accessibility standards for visibility. The arrow positioning is good, pointing to the enemy, but the background removal has some jagged edges compared to what Photoshop or Remove.bg would produce."
    },
    {
        "rating": 3,
        "feedback": "YouTube Studio analytics show that thumbnails with text on both top and bottom have 15% lower CTR than those with concentrated text in one area. This splits attention between multiple text elements. The character stands out well with background removal, but the red arrow blends with the game environment too much. Try studying how Markiplier structures his gaming thumbnails."
    },
    
    # 2-star feedback examples
    {
        "rating": 2,
        "feedback": "YouTube's Creator Academy specifically recommends against cluttered thumbnails. This has too many arrows (5+) which creates visual confusion. According to TubeBuddy data, thumbnails with 1-2 focal points outperform busy designs by 23%. The text is positioned correctly but the font choice lacks impact compared to top gaming channels."
    },
    {
        "rating": 2,
        "feedback": "The text is difficult to read against the background. The arrow positioning doesn't align with what was requested in the prompt. The font size is too small when viewed on mobile devices, which account for 70% of YouTube views according to platform statistics."
    },
    
    # 1-star feedback examples
    {
        "rating": 1,
        "feedback": "The background wasn't removed properly despite being specified. In 2023, clean foreground isolation is essential - channels with professional thumbnail editing see up to 40% higher CTR according to vidIQ statistics. The yellow text blends into the background instead of standing out, and the arrow positioning doesn't create a clear visual hierarchy."
    },
    {
        "rating": 1,
        "feedback": "This thumbnail ignores YouTube Studio's own best practices guidelines. The text is nearly invisible against the busy background, there's no clear focal point, and the overall composition lacks contrast. According to Morning Fame analytics, thumbnails with poor text contrast see 53% lower CTR than high-contrast alternatives."
    }
]

def generate_mock_thumbnail_data():
    """Generate fake thumbnail data for database population"""
    thumbnail_ids = []
    
    # Create mock timestamps starting from 30 days ago
    base_time = datetime.now() - timedelta(days=30)
    
    for i, prompt in enumerate(SAMPLE_PROMPTS):
        # Generate unique ID
        thumbnail_id = str(uuid.uuid4())
        thumbnail_ids.append(thumbnail_id)
        
        # Generate fake paths
        unique_filename = f"{thumbnail_id}.jpg"
        original_path = f'/uploads/{unique_filename}'
        thumbnail_path = f'/thumbnails/ai_thumbnail_{unique_filename}'
        
        # Create mock properties based on prompt
        style = "gaming" if "game" in prompt.lower() else "vlog"
        if "tutorial" in prompt.lower():
            style = "tutorial"
        elif "review" in prompt.lower():
            style = "review"
        elif "reaction" in prompt.lower():
            style = "reaction"
            
        properties = {
            "style": style,
            "text_overlay": prompt.split("'")[1] if "'" in prompt else "",
            "visual_elements": ["arrows"] if "arrow" in prompt.lower() else [],
            "color_scheme": ["red", "yellow"] if "red" in prompt.lower() else ["blue", "white"],
        }
        
        # Add to database with timestamp that increases with each entry (for realistic history)
        timestamp = (base_time + timedelta(days=i, hours=i*3)).isoformat()
        
        db.conn.execute(
            "INSERT INTO thumbnails VALUES (?, ?, ?, ?, ?, ?)",
            (
                thumbnail_id,
                original_path,
                thumbnail_path,
                prompt,
                json.dumps(properties),
                timestamp
            )
        )
    
    db.conn.commit()
    return thumbnail_ids

def add_feedback_data(thumbnail_ids):
    """Add feedback data to the thumbnails"""
    # Create mock timestamps starting from 25 days ago (after thumbnails were "created")
    base_time = datetime.now() - timedelta(days=25)
    
    # Match feedback to thumbnails
    for i, thumbnail_id in enumerate(thumbnail_ids):
        # Select feedback based on index position
        feedback_index = i % len(FEEDBACK_DATA)
        feedback = FEEDBACK_DATA[feedback_index]
        
        # Add timestamp that increases with each entry
        timestamp = (base_time + timedelta(days=i, hours=i*2)).isoformat()
        
        db.conn.execute(
            "INSERT INTO feedback (thumbnail_id, rating, feedback_text, created_at) VALUES (?, ?, ?, ?)",
            (thumbnail_id, feedback["rating"], feedback["feedback"], timestamp)
        )
    
    db.conn.commit()
    print(f"Added {len(thumbnail_ids)} feedback entries to the database")

def main():
    print("Populating database with training data...")
    
    # First check if database already has feedback data
    cursor = db.conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM feedback")
    feedback_count = cursor.fetchone()[0]
    
    if feedback_count > 0:
        print(f"Database already contains {feedback_count} feedback entries.")
        choice = input("Do you want to add more training data anyway? (y/n): ")
        if choice.lower() != 'y':
            print("Exiting without changes.")
            return
    
    # Generate mock thumbnails and add feedback
    thumbnail_ids = generate_mock_thumbnail_data()
    add_feedback_data(thumbnail_ids)
    
    print("Database populated successfully!")
    print("You can now run training with: python train_models.py")

if __name__ == "__main__":
    main()