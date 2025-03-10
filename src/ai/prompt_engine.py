import re
import json
from typing import Dict, List, Any, Tuple
import numpy as np

class PromptEngine:
    """Processes natural language prompts for thumbnail generation"""
    
    def __init__(self):
        self.thumbnail_styles = {
            "gaming": ["game", "gaming", "streamer", "playthrough", "minecraft", "fortnite"],
            "vlog": ["vlog", "daily", "lifestyle", "travel", "experience", "journey"],
            "tutorial": ["how to", "tutorial", "guide", "learn", "step by step", "explained"],
            "reaction": ["reaction", "reacting", "react", "shocked", "surprised"],
            "review": ["review", "analyzing", "opinion", "thoughts on"],
            "educational": ["educational", "facts", "science", "history", "learning"],
        }
        
        self.emotional_tones = {
            "excited": ["amazing", "awesome", "incredible", "mind-blowing", "exciting"],
            "shocked": ["shocking", "unbelievable", "you won't believe", "shocking truth"],
            "curious": ["mysterious", "secret", "revealed", "hidden", "discover"],
            "urgent": ["urgent", "warning", "alert", "important", "must see"],
            "funny": ["funny", "hilarious", "comedy", "laugh", "humor"],
        }
        
        self.visual_elements = {
            "arrows": ["pointing", "highlight", "arrow", "direction"],
            "circles": ["circle", "spotlight", "focus on", "zoom", "emphasize"],
            "text_overlay": ["caption", "title", "text", "heading", "words"],
            "face_expressions": ["surprised face", "shocked expression", "reaction face"],
            "thumbnail_composition": ["side by side", "before after", "comparison", "top view"]
        }
    
    def analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        """Analyze user prompt to extract thumbnail generation parameters with reasoning"""
        prompt = prompt.lower()
        
        # Extract style
        style, style_reasoning = self._extract_style(prompt)
        
        # Extract emotional tone
        tone, tone_reasoning = self._extract_tone(prompt)
        
        # Extract visual elements
        visuals, visuals_reasoning = self._extract_visuals(prompt)
        
        # Extract color preferences
        colors, color_reasoning = self._extract_colors(prompt)
        
        # Extract content focus
        content_focus, focus_reasoning = self._extract_content_focus(prompt)
        
        # Determine if specific people/faces are mentioned
        faces_mentioned, faces_reasoning = self._extract_faces_mentioned(prompt)
        
        # Look for specific text to include
        text_to_include, text_reasoning = self._extract_text_to_include(prompt)
        
        # Add new features
        positions, position_reasoning = self._extract_position_instructions(prompt)
        text_alignment, alignment_reasoning = self._extract_text_alignment(prompt)
        bg_removal, bg_reasoning = self._extract_background_removal(prompt)
        
        # Add character and enemy positions
        char_enemy_positions, char_enemy_reasoning = self._extract_character_enemy_positions(prompt)
        
        # Add text styling
        text_styling, styling_reasoning = self._extract_text_styling(prompt)
        
        # Generate thumbnail properties based on analysis
        thumbnail_properties = {
            "style": style,
            "style_reasoning": style_reasoning,
            "tone": tone,
            "tone_reasoning": tone_reasoning,
            "visual_elements": visuals,
            "visuals_reasoning": visuals_reasoning,
            "color_scheme": colors,
            "color_reasoning": color_reasoning,
            "content_focus": content_focus,
            "focus_reasoning": focus_reasoning,
            "faces_focus": faces_mentioned,
            "faces_reasoning": faces_reasoning,
            "text_overlay": text_to_include,
            "text_reasoning": text_reasoning,
            "positions": positions,
            "position_reasoning": position_reasoning,
            "text_alignment": text_alignment,
            "alignment_reasoning": alignment_reasoning,
            "remove_background": bg_removal,
            "bg_reasoning": bg_reasoning,
            "char_enemy_positions": char_enemy_positions,
            "char_enemy_reasoning": char_enemy_reasoning,
            "text_styling": text_styling,
            "styling_reasoning": styling_reasoning,
            "raw_prompt": prompt,
        }
        
        # Add a human-like explanation of the design approach
        thumbnail_properties["design_approach"] = self._generate_design_approach(thumbnail_properties)
        
        return thumbnail_properties

    def _generate_design_approach(self, properties):
        """Generate a human-like explanation of the design approach"""
        approach = f"I'll create a {properties['style']} style thumbnail "
        
        if properties['tone']:
            approach += f"with a {properties['tone']} emotional tone. "
        else:
            approach += ". "
            
        if properties['visual_elements']:
            elements = ", ".join(properties['visual_elements'])
            approach += f"I'll add {elements} to grab attention. "
            
        if properties['color_scheme']:
            colors = ", ".join(properties['color_scheme'])
            approach += f"Using {colors} colors for visual impact. "
            
        if properties['faces_focus']:
            approach += "I'll highlight faces in the image for stronger emotional connection. "
            
        if properties['text_overlay']:
            approach += f"Adding text overlay: '{properties['text_overlay']}'. "
            
        approach += "This combination will create an eye-catching thumbnail that drives clicks and views."
        
        return approach
    
    def _extract_style(self, prompt: str) -> Tuple[str, str]:
        """Determine the thumbnail style based on keywords in the prompt"""
        style_scores = {}
        
        for style, keywords in self.thumbnail_styles.items():
            score = 0
            for keyword in keywords:
                if keyword in prompt:
                    score += 1
            
            style_scores[style] = score
        
        # Get style with highest score
        if max(style_scores.values()) > 0:
            selected_style = max(style_scores, key=style_scores.get)
            reasoning = f"Detected '{selected_style}' style based on keywords in the prompt."
        else:
            # Default style if nothing detected
            selected_style = "vlog"
            reasoning = "No specific style keywords detected, defaulting to vlog style."
        
        return selected_style, reasoning
    
    def _extract_tone(self, prompt: str) -> Tuple[str, str]:
        """Extract emotional tone from prompt"""
        tone_scores = {}
        
        for tone, keywords in self.emotional_tones.items():
            score = 0
            for keyword in keywords:
                if keyword in prompt:
                    score += 1
            
            tone_scores[tone] = score
        
        # Get tone with highest score
        if max(tone_scores.values()) > 0:
            selected_tone = max(tone_scores, key=tone_scores.get)
            reasoning = f"Detected '{selected_tone}' emotional tone based on keywords in the prompt."
        else:
            # Default tone if nothing detected
            selected_tone = "excited"
            reasoning = "No specific tone keywords detected, defaulting to excited tone."
        
        return selected_tone, reasoning
    
    def _extract_visuals(self, prompt: str) -> Tuple[List[str], str]:
        """Extract visual elements to include from prompt"""
        requested_visuals = []
        detected_keywords = []
        
        for visual, keywords in self.visual_elements.items():
            for keyword in keywords:
                if keyword in prompt:
                    requested_visuals.append(visual)
                    detected_keywords.append(keyword)
                    break
        
        if requested_visuals:
            reasoning = f"Adding {', '.join(requested_visuals)} based on detected keywords: {', '.join(detected_keywords)}."
        else:
            reasoning = "No specific visual element keywords detected."
        
        return requested_visuals, reasoning
    
    def _extract_colors(self, prompt: str) -> Tuple[List[str], str]:
        """Extract color preferences from prompt"""
        colors = []
        
        # Common colors to detect
        color_list = ["red", "blue", "green", "yellow", "orange", "purple", 
                     "pink", "black", "white", "dark", "light", "vibrant", 
                     "neon", "pastel", "colorful"]
        
        for color in color_list:
            if color in prompt:
                colors.append(color)
        
        if colors:
            reasoning = f"Using {', '.join(colors)} colors based on prompt keywords."
        else:
            reasoning = "No specific color keywords detected."
        
        return colors, reasoning
    
    def _extract_content_focus(self, prompt: str) -> Tuple[str, str]:
        """Determine the main content focus"""
        if "product" in prompt or "item" in prompt or "review" in prompt:
            focus = "product"
            reasoning = "Content appears to be product-focused based on keywords."
        elif "face" in prompt or "reaction" in prompt or "person" in prompt:
            focus = "person"
            reasoning = "Content appears to be person/face-focused based on keywords."
        elif "comparison" in prompt or "versus" in prompt or " vs " in prompt:
            focus = "comparison"
            reasoning = "Content appears to be a comparison based on keywords."
        elif "scenery" in prompt or "landscape" in prompt:
            focus = "scenery"
            reasoning = "Content appears to be scenery/landscape focused based on keywords."
        elif "text" in prompt or "quote" in prompt:
            focus = "text_focused"
            reasoning = "Content appears to be text-focused based on keywords."
        else:
            focus = "general"
            reasoning = "No specific content focus detected, using general approach."
        
        return focus, reasoning
    
    def _extract_faces_mentioned(self, prompt: str) -> Tuple[bool, str]:
        """Determine if faces should be a focus"""
        face_keywords = ["face", "person", "people", "reaction", "surprised", 
                         "shocked", "expression", "youtuber", "streamer"]
        
        found_keywords = []
        for keyword in face_keywords:
            if keyword in prompt:
                found_keywords.append(keyword)
        
        if found_keywords:
            return True, f"Face focus suggested by keywords: {', '.join(found_keywords)}"
        
        return False, "No face-related keywords detected."
    
    def _extract_text_to_include(self, prompt: str) -> Tuple[str, str]:
        """Extract specific text to include in the thumbnail"""
        # Look for text in quotes 
        quote_match = re.search(r'"([^"]*)"', prompt) or re.search(r"'([^']*)'", prompt)
        if quote_match:
            # Return the exact text as found in quotes (preserving case)
            return quote_match.group(1), "Found text in quotes."
        
        # Look for text after phrases like "with text" or "add text"
        text_match = re.search(r"with text (?:saying |that says |reading |)['\"](.*?)['\"]", prompt) or \
                    re.search(r"add text ['\"](.*?)['\"]", prompt) or \
                    re.search(r"text saying ['\"](.*?)['\"]", prompt)
        
        if text_match:
            return text_match.group(1), "Found text following a text indicator phrase."
        
        # If no specific text found but text is mentioned, extract a title from the prompt
        if "text" in prompt:
            # Remove common instruction phrases to extract potential title
            cleaned = re.sub(r"make a thumbnail (for|with|that has|showing)", "", prompt)
            cleaned = re.sub(r"create a (youtube |)thumbnail", "", cleaned)
            cleaned = re.sub(r"with text", "", cleaned)
            cleaned = re.sub(r"add text", "", cleaned)
            
            # Capitalize the first letter of each word for a title
            title_words = [word.capitalize() for word in cleaned.strip().split()[:6]]
            if title_words:
                return " ".join(title_words), "Generated title from prompt content."
        
        # Default - no specific text found
        return "", "No specific text found in the prompt."
    
    def _extract_position_instructions(self, prompt: str) -> Tuple[Dict[str, Any], str]:
        """Extract positioning instructions for elements"""
        positions = {}
        reasoning = "No specific positioning instructions detected."
        
        # Text positioning
        text_pos_match = re.search(r'text (on|at|in) (the )?(top|bottom|left|right|center|corner)', prompt)
        if text_pos_match:
            position = text_pos_match.group(3)
            positions['text'] = position
            reasoning = f"Detected text position instruction: {position}"
        
        # Arrow positioning
        arrow_pos_match = re.search(r'arrows? (on|at|in|pointing to) (the )?(top|bottom|left|right|center|corner)', prompt)
        if arrow_pos_match:
            position = arrow_pos_match.group(3)
            positions['arrow'] = position
            if reasoning == "No specific positioning instructions detected.":
                reasoning = f"Detected arrow position instruction: {position}"
            else:
                reasoning += f", arrow position: {position}"
        
        # Character/subject positioning
        char_pos_match = re.search(r'(character|person|face|subject) (on|at|in) (the )?(top|bottom|left|right|center|corner)', prompt)
        if char_pos_match:
            position = char_pos_match.group(4)
            positions['character'] = position
            if reasoning == "No specific positioning instructions detected.":
                reasoning = f"Detected character position instruction: {position}"
            else:
                reasoning += f", character position: {position}"
        
        return positions, reasoning

    def _extract_text_alignment(self, prompt: str) -> Tuple[str, str]:
        """Extract text alignment instructions"""
        alignment = "center"  # Default alignment
        reasoning = "No specific text alignment detected, using center alignment by default."
        
        # Look for alignment keywords
        if re.search(r'text (aligned|alignment) (to )?(left|right|center)', prompt):
            match = re.search(r'text (aligned|alignment) (to )?(left|right|center)', prompt)
            alignment = match.group(3)
            reasoning = f"Text alignment set to {alignment} as specified in prompt."
        elif "left align" in prompt:
            alignment = "left" 
            reasoning = "Text alignment set to left as specified in prompt."
        elif "right align" in prompt:
            alignment = "right"
            reasoning = "Text alignment set to right as specified in prompt."
        elif "center align" in prompt or "centered text" in prompt:
            alignment = "center"
            reasoning = "Text alignment set to center as specified in prompt."
        
        return alignment, reasoning

    def _extract_background_removal(self, prompt: str) -> Tuple[bool, str]:
        """Detect if background removal is requested"""
        bg_removal = False
        reasoning = "No background removal requested."
        
        bg_keywords = [
            "remove background", "no background", "transparent background",
            "cut out", "extract", "isolate", "silhouette", "background removed", 
            "with the background removed"  # Added this phrase
        ]
        
        for keyword in bg_keywords:
            if keyword in prompt:
                bg_removal = True
                reasoning = f"Background removal detected based on keyword: '{keyword}'"
                break
        
        return bg_removal, reasoning

    def _extract_character_enemy_positions(self, prompt: str) -> Tuple[Dict[str, str], str]:
        positions = {}
        reasoning = "No character or enemy position instructions detected."
        
        # Character positioning
        char_pos_match = re.search(r'(character|my character|hero) (?:on|at|to) (?:the )?(left|right)', prompt)
        if char_pos_match:
            positions['character'] = char_pos_match.group(2)
            reasoning = f"Character positioned at {char_pos_match.group(2)}"
        
        # Enemy positioning
        enemy_pos_match = re.search(r'(enemy|boss|monster|opponent) (?:on|at|to) (?:the )?(left|right)', prompt)
        if enemy_pos_match:
            positions['enemy'] = enemy_pos_match.group(2)
            if 'character' in positions:
                reasoning += f", enemy positioned at {enemy_pos_match.group(2)}"
            else:
                reasoning = f"Enemy positioned at {enemy_pos_match.group(2)}"
        
        return positions, reasoning

    def _extract_text_styling(self, prompt: str) -> Tuple[Dict[str, Any], str]:
        """Extract text styling instructions"""
        styling = {
            "style": "",
            "size": "normal"
        }
        reasoning = "No specific text styling detected."
        
        # Check for text styling keywords
        if "bold" in prompt.lower():
            styling["style"] += "bold"
            reasoning = "Using bold text as specified in prompt."
        
        if "italic" in prompt.lower():
            styling["style"] += " italic"
            reasoning = (reasoning if reasoning == "No specific text styling detected." else reasoning[:-1]) + " and italic text as specified in prompt."
        
        # Check for text size
        if "large text" in prompt.lower() or "big text" in prompt.lower():
            styling["size"] = "large"
            reasoning += " Using large text size."
        elif "small text" in prompt.lower():
            styling["size"] = "small"
            reasoning += " Using small text size."
        
        return styling, reasoning