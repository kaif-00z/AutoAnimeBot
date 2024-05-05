[![Stars](https://img.shields.io/github/stars/kaif-00z/AutoAnimeBot?style=flat-square&color=yellow)](https://github.com/kaif-00z/AutoAnimeBot/stargazers)
[![Forks](https://img.shields.io/github/forks/kaif-00z/AutoAnimeBot?style=flat-square&color=orange)](https://github.com/kaif-00z/AutoAnimeBotfork)
[![Python](https://img.shields.io/badge/Python-v3.10.4-blue)](https://www.python.org/)
[![CodeFactor](https://www.codefactor.io/repository/github/kaif-00z/autoanimebot/badge/main)](https://www.codefactor.io/repository/github/kaif-00z/autoanimebot/overview/main)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/kaif-00z/AutoAnimeBot/graphs/commit-activity)
[![Contributors](https://img.shields.io/github/contributors/kaif-00z/AutoAnimeBot?style=flat-square&color=green)](https://github.com/kaif-00z/AutoAnimeBot/graphs/contributors)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](https://makeapullrequest.com)
[![License](https://img.shields.io/badge/license-GPLv3-blue)](https://github.com/kaif-00z/AutoAnimeBot/blob/main/LICENSE)   
[![Sparkline](https://stars.medv.io/kaif-00z/AutoAnimeBot.svg)](https://stars.medv.io/kaif-00z/AutoAnimeBot)

## Description Of Latest Update

- ReWritten Whole Program (Fully OOPs Based)
- Optimized Core
- Added Heroku Support
- Added Button Upload Support (File Store)
- <details><summary>Click Here To See How Button Upload Look.</summary><img src="https://graph.org/file/fbe1bf09ad2526f9386e5.jpg" alt="btnul"/></details>
- Added Custom CRF Support

## Contributing

- Any Sort of Contributions are Welcomed!
- Try To Resove Any Task From ToDo List!

## How to deploy?
<p><a href="https://youtu.be/n1yG6HabW28"> <img src="https://img.shields.io/badge/See%20Video-black?style=for-the-badge&logo=YouTube" width="160""/></a></p>

### Fork Repo Then click on below button of ur fork repo.
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

## Developer Note

- If Hosted On Heroku Then Encoding Of Per Episode Will Take Around 20mins.
- If You Don't Have High End VPS like 8vcpu or 32GiB RAM So Don't Deploy This Bot.
- You Can Customize FFMPEG Code If You Know What You Are Doing.

## Environmental Variable

### REQUIRED VARIABLES

- `BOT_TOKEN` - Get This From @Botfather In Telegram.

- `REDIS_URI` - Get This From redis.com

- `REDIS_PASSWORD` - Get This From redis.com

- `MAIN_CHANNEL` - ID of Channel Where Anime Will Upload.

- `CLOUD_CHANNEL` - ID of Channel Where Samples And Screenshots Of Anime Will Be Uploaded.

- `LOG_CHANNEL` - ID of Channel Where Status Of Proccesses Will Be Shown.

- `OWNER` - ID of Owner.

### OPTIONAL VARIABLES

- `BACKUP_CHANNEL` - ID of Channel Where Anime Will Be Saved As BackUP if You Are Using Button Upload Option Then Make Sure To SET Backup Channel.

- `THUMBNAIL` - JPG/PNG Link of Thumbnail FIle.

- `FFMPEG` - You Can Set Custom Path Of ffmpeg if u want, default is `ffmpeg`.

- `SEND_SCHEDULE` - `True/False` Send Schedule of Upcoming Anime of that day at 00:30 **IST**, default is `False`.

- `RESTART_EVERDAY` - `True/False` It Will Restart The Bot Everyday At 00:30 **IST**, default is `True`.

- `CRF` - Less CRF == High Quality, More Size , More CRF == Low Quality, Less Size, CRF Range = 20-51.

## Deployment In VPS

`git clone https://github.com/kaif-00z/AutoAnimeBot.git`

`nano .env` configure env as per [this](https://github.com/kaif-00z/AutoAnimeBot/blob/main/.sample.env) or  using [this](https://github.com/kaif-00z/AutoAnimeBot/blob/main/auto_env_gen.py).

`bash pkg.sh`

`bash run.sh`

## Commands

[![Comand](https://graph.org/file/82176674097989fae68d4.png)](https://github.com/kaif-00z/AutoAnimeBot/)

**Uploading of Ongoing Animes Is Automatic**

## About

- This Bot Is Currently Running In [This Channel](https://telegram.dog/Ongoing_Animes_Flares) .

## Donate

- [Contact me on Telegram](t.me/kaif_00z) if you would like to donate me for my work!
