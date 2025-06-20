"""Example of integrating AWS services with pygame."""

import pygame
import boto3
import json
import os
from datetime import datetime


class AwsGameExample:
    """Example class showing AWS integration with pygame."""
    
    def __init__(self, width=800, height=600):
        """Initialize the example.
        
        Args:
            width (int): Screen width
            height (int): Screen height
        """
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("AWS Porker - AWS Integration Example")
        self.clock = pygame.time.Clock()
        self.running = False
        self.fps = 60
        self.font = pygame.font.SysFont(None, 24)
        self.background_color = (50, 50, 50)  # Dark gray background
        
        # AWS related attributes
        self.s3_client = boto3.client('s3')
        self.buckets = []
        self.aws_data_loaded = False
        self.loading_message = "Loading AWS data..."
        
    def load_aws_data(self):
        """Load data from AWS services."""
        try:
            # List S3 buckets
            response = self.s3_client.list_buckets()
            self.buckets = [bucket['Name'] for bucket in response['Buckets']]
            self.aws_data_loaded = True
        except Exception as e:
            self.loading_message = f"Error loading AWS data: {str(e)}"
            
    def save_game_state(self, bucket_name, game_state):
        """Save game state to S3.
        
        Args:
            bucket_name (str): S3 bucket name
            game_state (dict): Game state to save
        """
        try:
            # Add timestamp to game state
            game_state['timestamp'] = datetime.now().isoformat()
            
            # Convert game state to JSON
            game_state_json = json.dumps(game_state)
            
            # Save to S3
            self.s3_client.put_object(
                Bucket=bucket_name,
                Key=f"game_states/save_{datetime.now().strftime('%Y%m%d%H%M%S')}.json",
                Body=game_state_json
            )
            return True
        except Exception as e:
            print(f"Error saving game state: {str(e)}")
            return False
            
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Add more event handling here
                
    def update(self):
        """Update game state."""
        if not self.aws_data_loaded:
            self.load_aws_data()
        
    def render(self):
        """Render the example."""
        # Clear the screen
        self.screen.fill(self.background_color)
        
        # Draw AWS data
        if self.aws_data_loaded:
            # Draw title
            title_text = self.font.render("AWS S3 Buckets:", True, (255, 255, 255))
            self.screen.blit(title_text, (20, 20))
            
            # Draw bucket list
            if self.buckets:
                for i, bucket in enumerate(self.buckets):
                    bucket_text = self.font.render(bucket, True, (200, 200, 200))
                    self.screen.blit(bucket_text, (40, 60 + i * 30))
            else:
                no_buckets_text = self.font.render("No buckets found", True, (200, 200, 200))
                self.screen.blit(no_buckets_text, (40, 60))
                
            # Draw instructions
            instructions = [
                "This example shows how to integrate AWS services with pygame.",
                "You can use AWS services to:",
                "- Store game assets in S3",
                "- Save game state to DynamoDB",
                "- Use Lambda for game logic",
                "- Implement multiplayer with API Gateway and WebSockets"
            ]
            
            for i, instruction in enumerate(instructions):
                instruction_text = self.font.render(instruction, True, (180, 180, 255))
                self.screen.blit(instruction_text, (20, 300 + i * 30))
        else:
            # Draw loading message
            loading_text = self.font.render(self.loading_message, True, (255, 255, 255))
            text_rect = loading_text.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(loading_text, text_rect)
        
        # Update the display
        pygame.display.flip()
        
    def run(self):
        """Run the example."""
        self.running = True
        
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(self.fps)
            
        pygame.quit()
        

def main():
    """Run the example."""
    example = AwsGameExample()
    example.run()
    
    
if __name__ == "__main__":
    main()
