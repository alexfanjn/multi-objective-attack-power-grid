## Multi-objective-attack-power-grid
The relevant codes of our work "**Revealing Structural and Functional Vulnerability of Power Grids to Cascading Failures**".

## Requirements

- python 3.6
- networkx
- numpy
- pypower

## Run the demo

For **NSGA-PG** attack:

```
python nsga2.py
```

For **NSGA-PG_{CN}** attack:

```
python nsga2_fresh_acc.py
```

For **LDV** attack:

```
python LDV_attack.py
```

For **reduce search space** attack and **risk-graph** attack:

```
python risk_graph.py
```

## Code Description

- **Attack.py**: implements the normal attack of a given attack list.
- **Graph.py**: implements the basic functions of power grids.
- **individual.py**: defines the individuals in evolution algorithms.
- **LDV_attack.py**: implements the LDV attack method.
- **nsga2.py**:  implements the NSGA-PG attack method.
- **nsga2_fresh_acc.py**: implements the NSGA-PG_{CN} attack method.
- **Power_Failure.py**:  implements the cascading failure process of power grids.
- **RG.py**: implements the relevant functions of risk-graph attack methods.
- **risk_graph.py**: implements the risk-graph method.
- **sinobject_ga.py**:  implements the single-objective genetic algorithm.

## Slides
The introduction slides can be found [here](https://github.com/alexfanjn/multi-objective-attack-power-grid/blob/master/Slides_Revealing%20Structural%20and%20Functional%20Vulnerability%20of%20Power%20Grids%20to%20Cascading%20Failures.pptx).


## Cite
For the details, you can take a look at the [paper](https://ieeexplore.ieee.org/abstract/document/9235529).  
If you find this work is helpful, please cite our paper. Thank you.

```
@ARTICLE{9235529,
  author={J. {Fang} and J. {Wu} and Z. {Zheng} and C. K. {Tse}},
  journal={IEEE Journal on Emerging and Selected Topics in Circuits and Systems}, 
  title={Revealing Structural and Functional Vulnerability of Power Grids to Cascading Failures}, 
  year={2021},
  volume={11},
  number={1},
  pages={133-143},
  doi={10.1109/JETCAS.2020.3033066}}
```
