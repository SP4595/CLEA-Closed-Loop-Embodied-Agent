# CLEA: Closed-Loop Embodied Agent

<div align="center">

[[Website]](https://sp4595.github.io/CLEA/)
[[Arxiv]](https://arxiv.org/abs/2503.00729)
[[PDF]](https://arxiv.org/pdf/2503.00729)
______________________________________________________________________


<img src = "images/intro.jpg" widtion = 40%>


</div>

Large Language Models (LLMs) exhibit remarkable capabilities in the hierarchical decomposition of complex tasks through semantic reasoning. However, their application in embodied systems faces challenges in ensuring reliable execution of subtask sequences and achieving one-shot success in long-term task completion. To address these limitations in dynamic environments, we propose Closed-Loop Embodied Agent (CLEA)---a novel architecture incorporating four specialized open-source LLMs with functional decoupling for closed-loop task management. The framework features two core innovations: (1) Interactive task planner that dynamically generates executable subtasks based on the environmental memory, and (2) Multimodal execution critic employing an evaluation framework to conduct a probabilistic assessment of action feasibility, triggering hierarchical re-planning mechanisms when environmental perturbations exceed preset thresholds. To validate CLEA's effectiveness, we conduct experiments in a real environment with manipulable objects, using two heterogeneous robots for object search, manipulation, and search-manipulation integration tasks. Across 12 task trials, CLEA outperforms the baseline model, achieving a 67.3\% improvement in success rate and a 52.8\% increase in task completion rate. These results demonstrate that CLEA significantly enhances the robustness of task planning and execution in dynamic environments.

In this repo, we provide CLEA (LLM Agent part) code.

# Installation
CLEA requires Python ≥ 3.10. We have tested on Ubuntu 22.04, Windows 11. You need to follow the instructions below to install CLEA.

## Python Install
```
git clone https://github.com/SP4595/CLEA-Closed-Loop-Embodied-Agent
cd CLEA-Closed-Loop-Embodied-Agent
pip install -r requirements.txt
pip install -e .
```
# Getting Started
To run the CLEA code, you first need to modify the `settings.yml` file. Update the **API key** and any other necessary information with your own credentials.  

After updating the file, you can run the code following commands (at `CLEA-Closed-Loop-Embodied-Agent` path):

```bash
python ./CLEA/Main/main.py
```

# Change API

If you want to apply CLEA to other environment, please change navigation points, task and object list in settings `settings.yml` and change the APIs in `./CLEA/API/API.py`. For API, please follow the format below (CLEA will autometically read these code!)

```python
def open(robot, openable_object) -> str:
    """
    <Description>
    ... Your description of your api
    </Description>
    <Params>
    ... Description of APIs
    </Params>
    """
    # ... Your code here ...
```

# Paper and Citation

If you find our work useful, please consider citing us! 

```bibtex
@misc{lei2025cleaclosedloopembodiedagent,
      title={CLEA: Closed-Loop Embodied Agent for Enhancing Task Execution in Dynamic Environments}, 
      author={Mingcong Lei and Ge Wang and Yiming Zhao and Zhixin Mai and Qing Zhao and Yao Guo and Zhen Li and Shuguang Cui and Yatong Han and Jinke Ren},
      year={2025},
      eprint={2503.00729},
      archivePrefix={arXiv},
      primaryClass={cs.RO},
      url={https://arxiv.org/abs/2503.00729}, 
}
```