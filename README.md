<div align="center">

<img src="assets/omniai-logo.png" width="72" alt="ZJU-OmniAI">

# Embodied-Omni

**A series of open-source embodied-AI projects from [ZJU-OmniAI](https://github.com/ZJU-OmniAI) — models that *observe*, *reason*, and *act* in the physical world.**

Long-horizon task planning · environment-state reasoning · self-reflection · real-robot deployment

<a href="https://github.com/ZJU-OmniAI/Embodied-Omni/stargazers"><img alt="Stars" src="https://img.shields.io/github/stars/ZJU-OmniAI/Embodied-Omni?style=flat&logo=github&color=181717"></a>
<a href="https://github.com/ZJU-OmniAI/Embodied-Omni/forks"><img alt="Forks" src="https://img.shields.io/github/forks/ZJU-OmniAI/Embodied-Omni?style=flat&logo=github&color=555555"></a>
<a href="./LICENSE"><img alt="License" src="https://img.shields.io/badge/License-Mulan_PSL_v2-yellow"></a>
<a href="https://arxiv.org/abs/2503.21696"><img alt="arXiv" src="https://img.shields.io/badge/Paper-arXiv-B31B1B?logo=arxiv&logoColor=B31B1B"></a>
<a href="https://aclanthology.org/2026.acl-long.1910/"><img alt="ACL 2026" src="https://img.shields.io/badge/ACL_2026-Main-EE3F24"></a>
<a href="https://huggingface.co/datasets/zwq2018/embodied_reasoner"><img alt="Hugging Face" src="https://img.shields.io/badge/Data_and_Models-Hugging_Face-FFD21E?logo=huggingface&amp;logoColor=FFD21E"></a>

**[Embodied-Reasoner](#-embodied-reasoner) · [Embodied-Navigator](#-embodied-navigator) · [Quick start](#-quick-start) · [Citation](#-citation)**

</div>

> [!NOTE]
> **This repository was renamed.** It was previously `zwq2018/embodied_reasoner` — the URL cited in the Embodied-Reasoner paper — and is now `ZJU-OmniAI/Embodied-Omni`, hosting the whole Embodied-Omni series. GitHub redirects the old URL here automatically, so existing links, clones, and remotes keep working.
> **Looking for Embodied-Reasoner? It now lives in [`embodied_reasoner/`](./embodied_reasoner/).**

---

## 🌏 Overview

Embodied intelligence needs more than a strong VLM: an agent has to *keep interacting* with the world, *remember* what it has already seen, *reason* about where things are, and *correct itself* when a plan fails. **Embodied-Omni** collects our work on exactly this loop, and releases it end to end — data engines, training recipes, evaluation harnesses, and real-robot deployment code.

Two projects live here today, covering the two halves of physical-world competence:

| Project | One-line summary | Embodiment & benchmark | Status |
|---|---|---|---|
| 🔍 **[Embodied-Reasoner](./embodied_reasoner/)** | An o1-style multimodal reasoning model for **interactive** tasks — search for hidden objects, manipulate and transport them, with explicit analysis, spatial reasoning, reflection, and planning. | Indoor agent in AI2-THOR (107 scenes) | **ACL 2026 Main** ✅ |
| 🧭 **[Embodied-Navigator](./embodied_navigator/)** | A vision-language **navigation** framework: the VLM points at a pixel instead of regressing coordinates, thinks only at critical nodes, compresses history into anchors, and is aligned with Two-Level GRPO. | Habitat R2R-CE / RxR-CE + Unitree Go2 quadruped | Paper coming soon 🚧 |

Common design principles across the series:

- **🧠 Reason where it matters** — explicit thinking (analysis, spatial reasoning, reflection, planning, verification) instead of blind action prediction.
- **🖼️ Interleaved multimodal context** — long observation–thought–action trajectories rather than single-image QA.
- **🔁 Iterative alignment** — imitation learning first, then self-exploration / reinforcement learning against environment feedback.
- **📦 Fully open** — synthesis engines, datasets, training scripts, evaluation code, and deployment services, not just weights.

---

## 🔍 Embodied-Reasoner

<p align="center">
  <img src="embodied_reasoner/assets/embodied_reasoner.JPG" width="88%" alt="Embodied-Reasoner">
</p>

<div align="center">

**Synergizing Visual Search, Reasoning, and Action for Embodied Interactive Tasks**

*ACL 2026 Main Conference*

[📄 Paper](https://aclanthology.org/2026.acl-long.1910/) · [📑 arXiv](https://arxiv.org/abs/2503.21696) · [🌐 Project page](https://embodied-reasoner.github.io) · [🤗 Dataset](https://huggingface.co/datasets/zwq2018/embodied_reasoner) · [📺 Talk (Bilibili)](https://www.bilibili.com/video/BV1Cs7Hz4ETk?t=1623.2) · [📂 Code](./embodied_reasoner/)

</div>

### 🎬 Demo

https://github.com/user-attachments/assets/da9c5b42-ab8e-4101-9ec0-a226590d23fc

<p align="center"><em>Embodied-Reasoner explores a room, reflects on what it has already checked, and finds hidden objects to complete a long-horizon instruction.</em></p>

### What it does

Given an instruction such as *"Locate the apple and put it in the microwave"*, the model receives only ego-centric images, and alternates between **thinking** and **acting** for dozens of turns:

- **👉 Deep reasoning** — analysis, spatial reasoning, reflection, planning, and verification, kept coherent across a whole episode.
- **👉 Interleaved multimodal processing** — long image–text interleaved histories, not one-shot perception.
- **👉 Environmental interaction** — autonomously observes, navigates, opens containers, and finds objects that are not visible at the start.
- **👉 Task and Trajectory Engine** — automatically synthesizes coherent *Observation–Thought–Action* trajectories over 107 indoor scenes, 2,100 interactive objects, and 2,600 containers.
- **👉 Open data** — [9.3k trajectories, 64k first-person images, and 8M thought tokens](https://huggingface.co/datasets/zwq2018/embodied_reasoner) on Hugging Face.

Training is a three-stage recipe — **imitation learning → self-exploration tuning → self-correction (reflection) tuning** — producing the Embodied-Interactor / Explorer / Reasoner checkpoints in 7B and 2B sizes.

### Results

Evaluated on 809 interactive test cases across 12 novel scenarios (success rate, search efficiency, and task completeness, all higher-is-better):

| Model | Success Rate | Search Efficiency | Task Completeness |
|---|---:|---:|---:|
| GPT-4o | 66.67% | 41.68% | 79.07% |
| Claude-3.7-Sonnet-thinking | 67.70% | 37.95% | 78.63% |
| GPT-o1 | 71.73% | 43.06% | 82.49% |
| Embodied-Interactor-7B *(stage 1)* | 25.46% | 24.75% | 53.67% |
| Embodied-Explorer-7B *(stage 2)* | 65.39% | 46.25% | 77.73% |
| **Embodied-Reasoner-7B** *(stage 3)* | **80.96%** | **55.07%** | **86.30%** |

Embodied-Reasoner exceeds OpenAI o1 by **+9%**, o3-mini by **+24%**, and Claude-3.7 by **+13%** success rate, with far fewer repeated searches and logical inconsistencies — and the advantage grows on the longest-horizon tasks. Real-world testing on a physical scene confirms the same behaviour: the model rules out surfaces it has already checked before opening the right cabinet, while o3-mini heads to the microwave before it has even found the coffee.

<p align="center">
  <img src="embodied_reasoner/assets/real_example.jpg" width="72%" alt="Real-world example">
</p>

➡️ **[Full README, training, evaluation, and data engine →](./embodied_reasoner/)**

---

## 🧭 Embodied-Navigator

<div align="center">

**Point, Think, Memorize, and Align for Efficient Embodied Navigation**

*"Point in pixels. Move in 3D. Think when needed. Remember what matters."*

[🌐 Project page](https://zju-omniai.github.io/Embodied-Navigator/) · [🤗 Model](https://huggingface.co/UnderTides/Embodied-Navigator-7B-GRPO) · [📂 Code](./embodied_navigator/) · [🔗 Standalone repo](https://github.com/ZJU-OmniAI/Embodied-Navigator)

</div>

### 🎬 Demo

https://github.com/user-attachments/assets/695b83b4-7672-4d77-ac5b-dc455258e036

<p align="center"><em>Model architecture and experimental results, plus zero-shot deployment on a Unitree Go2 quadruped.</em></p>

### What it does

Instead of asking a VLM to regress 3D coordinates or emit long strings of atomic actions, Embodied-Navigator lets it act as a **visual pointer**: pick one of four RGB views, point at a pixel, and let a SLAM controller execute the projected 3D waypoint.

<p align="center">
  <img src="embodied_navigator/docs/img/architecture.png" width="92%" alt="Embodied-Navigator architecture">
</p>

| Component | Mechanism | Effect |
|---|---|---|
| **Point** | Predict a 2D pixel waypoint, then project it to 3D through depth | Reuses the VLM's pretrained visual grounding; leaves metric geometry to deterministic modules |
| **Think** | Trigger chain-of-thought only at critical topological nodes | Reasoning on ~26% of steps matches dense CoT quality |
| **Memorize** | Anchor-Trajectory Memory: keep critical states as anchors, compress the rest into Space-Time Indicators | Preserves long-horizon topology without storing every frame |
| **Align** | Two-Level GRPO combining local action and global trajectory advantages | Closes the credit-assignment gap between final success and individual decisions |

### Results

Validation-unseen splits (NE lower is better; OS / SR / SPL / nDTW higher is better):

| Benchmark | Metric | Best prior* | **Embodied-Navigator** |
|---|---|---:|---:|
| R2R-CE | SR / SPL / NE | 64.3 / 58.5 / 4.05 | **66.2 / 58.8 / 3.85** |
| RxR-CE | SR / SPL / nDTW | 64.4 / 56.2 / 70.0 | **65.7 / 56.9 / 72.4** |
| Long-horizon subset (>12.5 m) | SR | 41.9 | **49.8** |
| Real world, zero-shot (100 trials) | SR | 53.0 | **60.0** |

<sub>*Best value per metric among StreamVLN, NavFoM, and DualVLN; see the [project README](./embodied_navigator/) for the full tables and ablations.</sub>

RL alignment lifts R2R-CE success from **55.7% (SFT only) to 66.2%**, while the policy needs only **~9 interactions per trajectory** and **16.6 s per task** on a single A800 — less than half the inference time of StreamVLN (37.5 s) or DualVLN (41.5 s). Real-robot deployment on the Unitree Go2 requires no robot-specific fine-tuning.

### 📺 Real-world deployment videos

Six representative zero-shot trials, drawn from the 100-episode real-world evaluation (click to play on GitHub, or watch them inline on the [project page](https://zju-omniai.github.io/Embodied-Navigator/)):

| Scene | Video | Notes |
|---|---|---|
| Cross-scenario | [cross-scenario.mp4](./embodied_navigator/docs/img/cross-scenario.mp4) | Long-horizon episode with an indoor→outdoor transition |
| Indoor hall | [hall.mp4](./embodied_navigator/docs/img/hall.mp4) | Long-corridor navigation with sparse reasoning |
| Meeting room | [meeting-room.mp4](./embodied_navigator/docs/img/meeting-room.mp4) | Cluttered indoor navigation |
| Outdoors | [outdoors.mp4](./embodied_navigator/docs/img/outdoors.mp4) | Open outdoor scene |
| Laboratory test area | [playground.mp4](./embodied_navigator/docs/img/playground.mp4) | Indoor lab navigation |
| Outdoors (**failure case**) | [outdoors-failed.mp4](./embodied_navigator/docs/img/outdoors-failed.mp4) | Target leaves all camera views; the policy stops prematurely |

➡️ **[Full README, training, evaluation, and robot serving →](./embodied_navigator/)**

---

## 📂 Repository layout

Each project is self-contained in its own top-level directory, with its own README, requirements, and scripts.

```text
Embodied-Omni/
├── embodied_reasoner/        # ACL 2026 · interactive embodied reasoning
│   ├── data_engine/          # Task & O1-style trajectory synthesis (AI2-THOR)
│   ├── data/                 # Dataset format and samples
│   ├── finetune/             # Three-stage training configs
│   ├── evaluate/             # 809-case interactive evaluation framework
│   ├── inference/            # Model inference
│   └── scripts/              # train.sh / eval.sh
├── embodied_navigator/       # Vision-language navigation
│   ├── src/agent/            # Policy, selective reasoning, Anchor-Trajectory Memory
│   ├── src/model/            # Navigation-adapted Qwen2.5-VL
│   ├── src/train/            # SFT + Two-Level GRPO
│   ├── src/env/ src/eval/    # Continuous-navigation env, NE/OS/SR/SPL/nDTW metrics
│   ├── src/server/           # FastAPI + ROS2 service for the Unitree Go2
│   ├── config/ scripts/      # Experiment configs and launch scripts
│   └── docs/                 # Project homepage, figures, deployment videos
└── assets/                   # Shared repository assets
```

## ⚡ Quick start

```shell
git clone https://github.com/ZJU-OmniAI/Embodied-Omni.git
cd Embodied-Omni

# Interactive embodied reasoning (AI2-THOR)
cd embodied_reasoner && cat README.md

# Vision-language navigation (Habitat / real robot)
cd ../embodied_navigator && cat README.md
```

Each project ships its own environment setup; do not mix them in one conda environment. Paths inside a project README are relative to that project directory.

## 📰 News

- **2026.08** — Embodied-Navigator joins the repository; `zwq2018/embodied_reasoner` becomes **`ZJU-OmniAI/Embodied-Omni`**, the home of the whole series.
- **2026.04** — Embodied-Reasoner accepted to **ACL 2026 Main Conference**.
- **2026.01** — [Invited talk @ 视觉语言导航](https://www.bilibili.com/video/BV149cjz5Es5/).
- **2025.05** — [Invited talk @ 智猩猩](https://www.bilibili.com/video/BV1Cs7Hz4ETk).
- **2025.03** — Embodied-Reasoner paper and dataset released.

## 📚 Citation

If you find this series useful, please cite the corresponding paper.

<details open>
<summary><b>Embodied-Reasoner</b> (ACL 2026)</summary>

```bibtex
@inproceedings{zhang-etal-2026-embodied,
    title = "Embodied-Reasoner: Synergizing Visual Search, Reasoning, and Action for Embodied Interactive Tasks",
    author = "Zhang, Wenqi  and
      Wang, Mengna  and
      Liu, Gangao  and
      Xu, Huixin  and
      Jiang, Yiwei  and
      Shen, Yongliang  and
      Hou, Guiyang  and
      Zheng, Zhe  and
      Zhang, Hang  and
      Li, Xin  and
      Liu, Jiajun  and
      Lu, Weiming  and
      Li, Peng  and
      Zhuang, Yueting",
    booktitle = "Proceedings of the 64th Annual Meeting of the {A}ssociation for {C}omputational {L}inguistics (Volume 1: Long Papers)",
    month = jul,
    year = "2026",
    address = "San Diego, California, United States",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2026.acl-long.1910/",
    doi = "10.18653/v1/2026.acl-long.1910",
    pages = "41178--41207",
    ISBN = "979-8-89176-390-6"
}
```

</details>

<details>
<summary><b>Embodied-Navigator</b></summary>

```bibtex
@inproceedings{feng2026embodiednavigator,
  title     = {Embodied-Navigator: Point, Think, Memorize, and Align
               for Efficient Embodied Navigation},
  author    = {Feng, Hongyan and Chen, Sunlai and Liu, Xuanyu and Pan, Miao and
               Xie, Yangfan and Cui, Yuxiang and Zhou, Zhongxiang and
               Xiong, Rong and Zhang, Wenqi and Yin, Jianwei and
               Zhuang, Yueting and Zhang, Xuhong},
  year      = {2026}
}
```

</details>

## 🌐 More from ZJU-OmniAI

| Repository | About |
|---|---|
| [Data-Copilot](https://github.com/ZJU-OmniAI/Data-Copilot) | Bridging billions of data and humans with autonomous workflow |
| [Agent-Pro](https://github.com/ZJU-OmniAI/Agent-Pro) | Learning to evolve via policy-level reflection and optimization |
| [GFT](https://github.com/ZJU-OmniAI/GFT) | From imitation to reward fine-tuning with unbiased group advantage |
| [vla-corrector](https://github.com/ZJU-OmniAI/vla-corrector) | Lightweight detect-and-correct inference for VLA models |
| [OMNEX-VL](https://github.com/ZJU-OmniAI/OMNEX-VL) | Hallucination-resistant MLLMs via caption feedback |
| [Awesome-Closed-Loop-VLA](https://github.com/ZJU-OmniAI/Awesome-Closed-Loop-VLA) · [Awesome-World-Model](https://github.com/ZJU-OmniAI/Awesome-World-Model) | Curated reading lists |

## 🙏 Acknowledgements

Embodied-Reasoner builds on [AI2-THOR](https://github.com/allenai/ai2thor) for simulation and [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory) for training. Embodied-Navigator builds on [Habitat-Lab](https://github.com/facebookresearch/habitat-lab) and [Qwen2.5-VL](https://github.com/QwenLM/Qwen2.5-VL). Thanks to all of these projects.

## 📬 Contact

Questions, issues, and collaborations are welcome — open an [issue](https://github.com/ZJU-OmniAI/Embodied-Omni/issues) or email us:

- Embodied-Reasoner — zhangwenqi@zju.edu.cn · lipeng@iscas.ac.cn
- Embodied-Navigator — hongyanfeng@zju.edu.cn · zhangxuhong@zju.edu.cn

## 📄 License

Released under the [Mulan PSL v2](./LICENSE) license.

---

<div align="center">

⭐ **If this work helps your research, please consider starring the repository.**

</div>
