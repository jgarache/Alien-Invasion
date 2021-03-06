import sys

from time import sleep

import pygame

from settings import Settings

from ship import Ship

from bullet import Bullet

from alien import Alien

from game_stats import GameStats


class AlienInvasion:
    """Overall class to manage game assets and behavior."""

    def __init__(self):
        """Init game, create game resources."""
        pygame.init()
        self.settings = Settings()

        """Windows mode"""
        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))

        """Full screen mode
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        """
        pygame.display.set_caption("Alien Invasion")

        # Create an instance to store game stats
        self.stats = GameStats(self)

        self.ship = Ship(self)

        # Set the background color
        self.bg_color = (230, 230, 230)

        # storage of all the bullets
        self.bullets = pygame.sprite.Group()

        # storage of all the aliens
        self.aliens = pygame.sprite.Group()

        # Creates a fleet of aliens on the screen
        self._create_fleet()

    def run_game(self):
        """Start the main loop for the game """
        while True:
            # Watch for keyboard and mouse events.
            self._check_events()

            if self.stats.game_active:
                # Updates bullets positions and number of bullets on the screen.
                self._update_bullets()

                # Redraw the screen during each pass through the loop
                self._update_screen()

                # Update the position of the aliens
                self._update_aliens()

    def _check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)

            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)

    def _check_keydown_events(self, event):
        """Responds to keypress"""
        if event.key == pygame.K_d:
            # move the ship to the right
            self.ship.moving_right = True

        elif event.key == pygame.K_a:
            # move the ship to the left
            self.ship.moving_left = True

        elif event.key == pygame.K_q:
            # quits and closes the game
            sys.exit()

        elif event.key == pygame.K_SPACE:
            # fires the bullets
            self._fire_bullet()

    def _check_keyup_events(self, event):
        """Responds to key releases"""
        if event.key == pygame.K_d:
            self.ship.moving_right = False
        elif event.key == pygame.K_a:
            self.ship.moving_left = False

    def _check_bullet_alien_collisions(self):
        """Checks and deletes bullet-alien collisions"""
        # Remove any bullet-alien collisions
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)

        if not self.aliens:
            # Destroy existing bullet and create new fleet
            self.bullets.empty()
            self._create_fleet()

    def _check_fleet_edges(self):
        """Responses accordingly if any aliens have reached an edge"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _check_aliens_bottom(self):
        """Check if aliens have hit the bottom of the screen"""
        screen_rect = self.screen.get_rect()

        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # Same behavior as if the ship got hit
                self._ship_hit()
                break

    def _fire_bullet(self):
        """Create a new bullet and add it to the bullets group"""
        if len(self.bullets) < self.settings.bullet_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        """Updates positions of the bullets and deletes old bullets"""

        # Updates the bullets position
        self.bullets.update()

        # Delete bullets that are off the screen
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        # Print the number of bullets on the screen
        # print(len(self.bullets))

        # Check bullet and alien collisions
        self._check_bullet_alien_collisions()

    def _update_screen(self):
        # Draws background
        self.screen.fill(self.settings.bg_color)

        # Draws ship
        self.ship.blitme()

        for bullet in self.bullets.sprites():
            bullet.draw_bullet()

        # Updates aliens position
        self.aliens.draw(self.screen)

        # Updates ships position
        self.ship.update()

        # Updates bullets positions
        self.bullets.update()

        # Make the most recently drawn screen visible.
        pygame.display.flip()

    def _update_aliens(self):
        """Check if the fleet is at an edge, then update positions of all aliens in the fleet"""
        self._check_fleet_edges()
        """Updates all aliens positions in the fleet"""
        self.aliens.update()

        # Alien and ship collision detection
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        # check if aliens have hit the bottom of the screen
        self._check_aliens_bottom()

    def _create_fleet(self):
        """Create the fleet of aliens."""
        # Make an alien
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)

        # Determine the num of rows of aliens and that fit on the screen
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - (3 * alien_height) - ship_height)

        number_rows = available_space_y // (2 * alien_height)

        # Create full fleet of aliens
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number, row_numbers):
        # Create an alien and place it in the row
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_numbers
        self.aliens.add(alien)

    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleets direction"""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed

        self.settings.fleet_direction *= -1

    def _ship_hit(self):
        """Responds to the ship getting hit"""
        if self.stats.ships_left > 0:
            self.stats.ships_left -= 1

            # Clear the screen after ship gets hit
            self.aliens.empty()
            self.bullets.empty()

            # create new fleet and move ship back to center
            self._create_fleet()
            self.ship.center_ship()

            # pause game to realize ship got destroyed
            sleep(1)
        else:
            self.stats.game_active = False


if __name__ == '__main__':
    # Make a game instance, and run the game.
    ai = AlienInvasion()
    ai.run_game()
