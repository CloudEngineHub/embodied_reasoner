# Embodied-Omni

A series of open-source projects on embodied reasoning and interaction from
[ZJU-OmniAI](https://github.com/ZJU-OmniAI).

> **📦 This repository was renamed.** It was previously `zwq2018/embodied_reasoner`
> — the URL cited in the Embodied-Reasoner paper — and is now
> `ZJU-OmniAI/Embodied-Omni`, hosting the whole Embodied-Omni series. GitHub
> redirects the old URL here automatically, so existing links, clones, and
> remotes keep working. **Looking for Embodied-Reasoner? It lives in
> [`embodied_reasoner/`](./embodied_reasoner/).**

## Projects

| Project | Description | Paper | Resources |
|---|---|---|---|
| [**Embodied-Reasoner**](./embodied_reasoner/) | A multimodal embodied model extending o1-style deep reasoning to interactive tasks in AI2-THOR: object search, manipulation, and transportation. ACL 2026 Main. | [ACL 2026](https://aclanthology.org/2026.acl-long.1910/) · [arXiv:2503.21696](https://arxiv.org/abs/2503.21696) | [Project page](https://embodied-reasoner.github.io) · [Dataset](https://huggingface.co/datasets/zwq2018/embodied_reasoner) |
| [**Embodied-Navigator**](./embodied_navigator/) | A unified vision-language navigation framework aligning high-level visual reasoning with low-level physical execution through pixel waypoint prediction, selective reasoning, trajectory memory, and hierarchical reinforcement learning. | Coming soon | [Project page](https://zju-omniai.github.io/Embodied-Navigator/) · [Model](https://huggingface.co/UnderTides/Embodied-Navigator-7B-GRPO) |

## Repository layout

Each project is self-contained in its own top-level directory, with its own
README, requirements, and scripts. Clone the repository and `cd` into the
project you want:

```shell
git clone https://github.com/ZJU-OmniAI/Embodied-Omni.git
cd Embodied-Omni/embodied_reasoner
```

## Citation

If you find this work useful, please cite the corresponding paper. For
Embodied-Reasoner:

```
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

## License

Released under the [Mulan PSL v2](./LICENSE) license.
