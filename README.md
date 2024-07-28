## Sådan tilføjer du filer til dit dotfiles repository og pusher til origin master

### Installér Homebrew, Stow og Git
1. **Installér Homebrew (hvis ikke allerede installeret):**
    ```sh
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    ```

2. **Installér Stow og Git via Homebrew:**
    ```sh
    brew install stow git
    ```

### Administrer dotfiles med Git og Stow
1. **Naviger til dit dotfiles directory:**
    ```sh
    cd path/to/your/dotfiles
    ```

2. **Tilføj nye filer eller ændringer til staging area:**
    ```sh
    git add .
    ```
    *Note: Du kan også tilføje specifikke filer ved at bruge `git add <filnavn>`.*

3. **Commit dine ændringer:**
    ```sh
    git commit -m "Beskrivende commit besked"
    ```

4. **Push dine ændringer til origin master:**
    ```sh
    git push origin master
    ```

5. **For at clone dit repository på en ny computer:**
    ```sh
    git clone https://github.com/<dit-brugernavn>/dotfiles.git
    ```

6. **Brug Stow til at administrere symlinks for dine dotfiles:**
    ```sh
    cd dotfiles
    stow <foldername>
    ```

### Tips
- **Check status:** Brug `git status` for at se hvilke filer der er ændret, og hvilke der er staged til commit.
- **Check commits:** Brug `git log` for at se tidligere commits og beskeder.

Husk at tilføje en `.gitignore` fil for at undgå at inkludere uønskede filer i dit repository.
