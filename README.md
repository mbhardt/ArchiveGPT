# ArchiveGPT

**ArchiveGPT** is an advanced, no-frills framework for deploying front-facing chatbots. It's like SillyTavern, but public-facing. The name comes from Blue Archive, because the first use of this framework was for a Blue Archive character. It is designed to be simple to deploy, and is *heavily* inspired by chikenuwu's Blue Archive chatbots MikaGPT and MiyakoGPT. His Github is [here](https://github.com/IsaacSohn) and I highly recommend you check out his work.

## Key Features
- **It's customizable**: ArchiveGPT is designed to be as plug-and-play as possible.
- **It's lightweight**: There's only 2 dependencies: Flask and Huggingface Transformers.

## Requirements
- Python 3.x.x
- Flask
- Huggingface Transformers
- An AI provider of your choice (e.g. OpenAI, together.ai, SambaNova)

## Installation
Clone the repository and install the required dependencies:

```bash
# Clone the repository
git clone https://github.com/mbhardt/ArchiveGPT.git
cd ArchiveGPT

# Install dependencies
pip install -r requirements.txt
```

## Quick Start
1. **Set up your deployment**:
   - Set up `config.yaml`
   - Write a system prompt for your character in `src/base_description.txt`
   - Add the images of your character in `src/public/assets/sprites/{normal/alt/alt2}`
   - Add the backgrounds you want in `src/public/assets/backgrounds`
   - Change `SPRITE_COUNT`, `MAX_IMAGES`, and `STUDENT_NAME` in `src/public/assets/script.js` (MAX_IMAGES refers to background images)
   - You're done!


2. **Run the server**:

```bash
cd src
python main.py
```

3. **Access the chatbot**:
   Open your browser and go to `http://localhost:{port set in config.yaml}`.

## Contributing
Contributions are welcome! Please fork the repository, create a new branch, and submit a pull request.

## License
This project is licensed under the GNU General Public License v3.0 (GPL-3.0). See `LICENSE` for details.