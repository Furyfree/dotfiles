{
  description = "Zenful nix-darwin system flake";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

    nix-darwin = {
      url = "github:LnL7/nix-darwin/master";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    nix-homebrew.url = "github:zhaofengli/nix-homebrew";

    homebrew-core = {
      url = "github:Homebrew/homebrew-core";
      flake = false;
    };

    homebrew-cask = {
      url = "github:Homebrew/homebrew-cask";
      flake = false;
    };
  };

  outputs =
    {
      self,
      nix-darwin,
      nixpkgs,
      nix-homebrew,
      homebrew-core,
      homebrew-cask,
      ...
    }:
    let
      system = "aarch64-darwin";
      user = "pby";

      configuration =
        { pkgs, ... }:
        {
          environment.systemPackages = with pkgs; [
            nixd
            nil
            # Packages are now managed through Homebrew
            # Add other packages as needed
          ];

          # Configure Homebrew packages using nix-darwin's homebrew module
          homebrew = {
            enable = true;
            onActivation.autoUpdate = true;
            onActivation.cleanup = "zap"; # Remove packages not in config
            brews = [
              "fzf" # Command-line fuzzy finder
              "vim" # Text editor
              "git" # Version control
              "htop" # Process viewer
              "mas" # Mac App Store CLI
              # "1password-cli" # 1Password CLI
              "bat" # Cat with syntax highlighting
              "eza" # Modern replacement for ls
              "fd" # Alternative to find
              "gh" # GitHub CLI
              "ripgrep" # Fast search tool
              "starship" # Cross-shell prompt
              "tmux" # Terminal multiplexer
              "tree" # Display directories as trees
              "zoxide" # Fast directory navigation
              "neovim" # Modern vim
              "neofetch" # System info
              "lazygit" # Terminal UI for git
              "fastfetch" # Fast system info
              "go" # Go programming language
              "jenv" # Java environment manager
              "kanata" # Keyboard remapper
              "lima" # Linux virtual machines
              "maven" # Java project management
              "node" # Node.js
              "pandoc" # Markup format converter
              "pyenv" # Python version management
              "stow" # Software organizer
              "yazi" # Terminal file manager
              "postgresql@16" # PostgreSQL database (LTS version)
              # "wireshark" # Network analyzer
              "lima-additional-guestagents"
              # "poetry"
              # Ladybird dependencies
              "autoconf"
              "autoconf-archive"
              "automake"
              "ccache"
              "cmake"
              "nasm"
              "ninja"
              "pkg-config"
              "llvm@20"
              "qt"

            ];
            casks = [
              "zen" # Browser
              "zed" # Code editor
              "visual-studio-code" # Code editor
              "wezterm" # Terminal
              "1password" # Password manager
              "raycast" # Launcher
              "alt-tab" # Window switcher
              # "cleanshot"                  # Screenshot tool
              "docker-desktop" # Containerization
              "font-fira-code-nerd-font" # Developer font
              "hammerspoon" # Automation
              "iina" # Media player
              "obsidian" # Note-taking
              "the-unarchiver" # Archive utility
              "airbuddy" # AirPods companion
              "aldente" # Battery charging limiter
              "balenaetcher" # OS image flasher
              "bartender" # Menu bar organizer
              "chatgpt" # OpenAI desktop app
              "claude" # Anthropic desktop app
              "cleanmymac" # Disk cleaner
              "discord" # Voice and text chat
              "itsycal" # Menu bar calendar
              "jetbrains-toolbox" # JetBrains tools manager
              "keepingyouawake" # Prevent sleep mode
              "linearmouse" # Mouse customization
              "mediamate" # UI replacement for controls
              "messenger" # Facebook Messenger
              "microsoft-auto-update" # Microsoft updater
              "microsoft-excel" # Spreadsheet software
              "microsoft-powerpoint" # Presentation software
              "microsoft-word" # Word processor
              "monitorcontrol" # External monitor control
              "obs" # Streaming software
              "proton-drive" # Proton Drive client
              "proton-mail" # Proton Mail client
              "protonvpn" # VPN client
              "signal" # Secure messaging
              "spotify" # Music streaming
              "utm" # Virtual machines UI
              "wireshark-app" # Network analyzer
              "oracle-jdk@21" # Java Development Kit (LTS version)
              "oracle-jdk" # Java Development Kit (latest version)
              "github" # GitHub Desktop client
              # "hyperkey" # Keyboard customization
              "lm-studio" # Language model studio
              "karabiner-elements" # Keyboard customization
            ];
            # Mac App Store apps
            masApps = {
              "Xcode" = 497799835;
              "WireGuard" = 1451685025;
              "1Password for Safari" = 1569813296;
              "Final Cut Pro" = 424389933;
              "rcmd" = 1596283165;
              "CrystalFetch ISO Downloader" = 6454431289;
            };
          };

          # macOS system settings
          system.defaults = {
            # Dock settings
            dock = {
              autohide = true; # Hide the dock
              autohide-delay = 0.0; # Remove delay when showing dock
              autohide-time-modifier = 0.0; # Remove animation when showing/hiding dock
              persistent-apps = [ ]; # Remove all apps from dock
              static-only = true; # Only show running apps
              tilesize = 16; # Set dock icon size to minimum (16px)
              magnification = false; # Disable magnification
              mineffect = "scale"; # Use scale effect for minimizing
              minimize-to-application = true; # Minimize windows into app icon
              showhidden = true; # Make hidden apps translucent
              show-recents = false; # Don't show recent applications
              launchanim = false; # Disable opening application animations
              orientation = "bottom"; # Position dock at the bottom
            };

            # Finder settings
            finder = {
              AppleShowAllExtensions = true; # Show all file extensions
              AppleShowAllFiles = true; # Show hidden files
              CreateDesktop = false; # Hide desktop icons
              FXEnableExtensionChangeWarning = false; # Don't warn when changing extension
              QuitMenuItem = true; # Allow quitting Finder
              ShowPathbar = true; # Show path bar
              ShowStatusBar = true; # Show status bar
              _FXShowPosixPathInTitle = true; # Show full POSIX path in window title
              FXPreferredViewStyle = "Nlsv"; # List view by default
            };

            # Global settings
            NSGlobalDomain = {
              AppleShowScrollBars = "Always"; # Always show scrollbars
              NSAutomaticCapitalizationEnabled = false; # Disable auto-capitalization
              NSAutomaticDashSubstitutionEnabled = false; # Disable smart dashes
              NSAutomaticPeriodSubstitutionEnabled = false; # Disable smart periods
              NSAutomaticQuoteSubstitutionEnabled = false; # Disable smart quotes
              NSAutomaticSpellingCorrectionEnabled = false; # Disable auto spelling correction
              NSNavPanelExpandedStateForSaveMode = true; # Expanded save panel
              NSNavPanelExpandedStateForSaveMode2 = true; # Expanded save panel
              "com.apple.keyboard.fnState" = false; # Use Mac-specific functions for F-keys
              "com.apple.sound.beep.volume" = 0.0; # Silent alert sound
              "com.apple.sound.beep.feedback" = 0; # Disable sound on volume change
              "com.apple.swipescrolldirection" = true; # Disable natural scrolling
              AppleKeyboardUIMode = 3; # Full keyboard access
              InitialKeyRepeat = 15; # Shorter delay for key repeat
              KeyRepeat = 2; # Faster key repeat
              NSWindowResizeTime = 0.001; # Fast window resizing
              NSScrollAnimationEnabled = false; # Disable smooth scrolling
            };

            # Trackpad settings
            trackpad = {
              Clicking = true; # Enable tap to click
              TrackpadRightClick = true; # Enable two-finger right click
              TrackpadThreeFingerDrag = false; # Enable three-finger drag
            };

            # Menu bar settings
            menuExtraClock = {
              Show24Hour = true; # Use 24-hour time
              ShowAMPM = false; # Hide AM/PM
              ShowDate = 1; # Show compact date
              ShowSeconds = true; # Show seconds
            };

            # Display and brightness settings
            CustomUserPreferences = {
              # Prevent display from automatically dimming on battery
              "com.apple.BezelServices" = {
                "kDim" = false;
              };

              # Disable automatic brightness adjustment
              "com.apple.CoreBrightness" = {
                "CBDisplaySelfSustainLevel" = 0;
                "CBUser-0" = {
                  "CBAdaptiveDisplayEnabled" = 0;
                };
              };

              # Disable ambient light sensor adjustments
              "com.apple.iokit.AmbientLightSensor" = {
                "Automatic Display Enabled" = false;
                "Automatic Keyboard Enabled" = false;
              };

              # Night Shift configuration
              "com.apple.CoreBrightness" = {
                "CBBlueLightReductionCCTTarget" = 2700; # Warmest setting (~2700K)
                "CBBlueLightReductionStatus" = {
                  "AutoBlueLight" = true; # Enable automatic Night Shift
                  "BlueLightReductionEnabled" = true; # Enable Night Shift
                  "BlueLightReductionMode" = 2; # 0: Off, 1: Manual, 2: Sunrise/Sunset
                  "BlueLightReductionSchedule" = {
                    "DawnTime" = 0; # Sunrise time (0 = use actual sunrise)
                    "DuskTime" = 0; # Sunset time (0 = use actual sunset)
                  };
                };
              };
            };
          };

          # Keyboard settings
          system.keyboard = {
            enableKeyMapping = true; # Enable keyboard remapping
            remapCapsLockToControl = false; # Don't remap Caps Lock (Raycast will handle it)
          };

          nix.settings.experimental-features = [
            "nix-command"
            "flakes"
          ];

          system.configurationRevision = self.rev or self.dirtyRev or null;
          system.stateVersion = 6;
          system.primaryUser = user;

          nixpkgs.hostPlatform = system;

          # Optional: user declaration (for completeness)
          users.users.${user} = {
            name = user;
            home = "/Users/${user}";
          };
        };
    in
    {
      darwinConfigurations."Patricks-MacBook-Pro" = nix-darwin.lib.darwinSystem {
        inherit system;
        modules = [
          configuration
          nix-homebrew.darwinModules.nix-homebrew
          {
            nix-homebrew = {
              enable = true;
              enableRosetta = true;
              user = user;
              taps = {
                "homebrew/core" = homebrew-core;
                "homebrew/cask" = homebrew-cask;
              };
              # Prevent manual brew installation outside of nix
              mutableTaps = false;
            };
          }
        ];
      };
    };
}
