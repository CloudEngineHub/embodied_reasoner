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
| [**Embodied-Reasoner**](./embodied_reasoner/) | A multimodal embodied model extending o1-style deep reasoning to interactive tasks in AI2-THOR: object search, manipulation, and transportation. ACL 2026 Main. | [arXiv:2503.21696](https://arxiv.org/abs/2503.21696) | [Project page](https://embodied-reasoner.github.io) · [Dataset](https://huggingface.co/datasets/zwq2018/embodied_reasoner) |

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
@article{embodied-reasoner,
    title   = {Embodied-Reasoner: Synergizing Visual Search, Reasoning, and Action for Embodied Interactive Tasks}, 
    author  = {Wenqi Zhang and Mengna Wang and Gangao Liu and Huixin Xu and Yiwei Jiang and Yongliang Shen and Guiyang Hou and Zhe Zheng and Hang Zhang and Xin Li and Weiming Lu and Peng Li and Yueting Zhuang},
    journal = {arXiv preprint arXiv:2503.21696},
    year    = {2025}
}
```

## License

Released under the [Mulan PSL v2](./LICENSE) license.
