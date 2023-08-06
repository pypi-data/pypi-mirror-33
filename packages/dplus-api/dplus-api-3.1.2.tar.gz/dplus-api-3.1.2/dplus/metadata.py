import math

_models_with_files_index_dict = {
    "PDB": 999,
    "AMP": 1000,
    "Scripted Geometry": 1001,
    "Scripted Model": 1002,
    "Scripted Symmetry": 1003,
}

def _type_to_int(type_str):

    #handle the specific cases of pdb etc

    if type_str in _models_with_files_index_dict:
        return _models_with_files_index_dict[type_str]

    #handle the ones loaded from that thing in the dumb fashion
    test = type_str.split(",")
    if test[0] != "":
        raise ValueError("Dll should be default (empty string) dll")
    try:
        type_int=int(test[1])
    except:
        raise ValueError("Model index not an integer number")

    return type_int


def _int_to_type(type_int):
    for key, value in _models_with_files_index_dict.items():
        if type_int ==value:
            return key
    return "," + str(type_int)



def extra_param_creator(name, defaultValue = 0.0,canBeInfinite=False, isAbsolute=False, brange=False, minval = 0.0, maxval = 0.0,  isIntegral=False, decimalPoints=6):
    return {
        "name": name,
        "defaultValue": defaultValue,
        "canBeInfinite": canBeInfinite,
        "isAbsolute": isAbsolute,
        # bool bRange=False
        "range": {"min": minval, "max": maxval},
        "isIntegral": isIntegral,
        "decimalPoints": decimalPoints,
    }

'''
	ModelInformation(const char *modelname = "Abstract Model - DO NOT USE",
					 int cat = -1, int ind = -1, bool layerbased = True,
					 int layerparams = 2, int minlayer = 1, int maxlayer = 2,
					 int exparams = 2, int disps = 0, bool gpu = False,
					 bool slow = False, bool calcff = False, bool datarequired = False) :
					 category(cat), modelIndex(ind),
					 isLayerBased(layerbased), nlp(layerparams), minLayers(minlayer),
					 maxLayers(maxlayer), nExtraParams(exparams), nDispParams(disps),
					 isGPUCompatible(gpu), isSlow(slow), ffImplemented(calcff)
'''

#(tName, -1, -1, False, 0, 0, 0, 8, 0, False /*TODO::GPU*/, True, True, True/*even though this is never used*/);


def create_hard_model(modelname,
					 cat = -1, ind = -1, layerbased = True,
					 numlayerparams = 2, minlayer = 1, maxlayer = 2,
					 exparams = 2, disps = 0, gpu = False,
					 slow = False, calcff = False, datarequired = False):
    return {
    "index": ind,
    "name": modelname,
    "category": cat,
    "gpuCompatible": gpu,
    "slow": slow,
    "ffImplemented": calcff,
    "isLayerBased": layerbased,
    "layers": {
        "min": minlayer,
        "max": maxlayer,
        "layerInfo": [],
        "params": []
    },
    "extraParams": []
    }

def pdbmodel():
    #TODO:
    # extraParamOptions[7].resize(RAD_SIZE);
    # extraParamOptions[7][0] = "No Solvent";
    # extraParamOptions[7][1] = "Van der Waals";
    # extraParamOptions[7][2] = "Empirical";
    # extraParamOptions[7][3] = "Calculated";
    # extraParamOptions[7][4] = "Dummy Atoms";
    pdbmod=create_hard_model("PDB", -1, 999, False, 0, 0, 0, 8, 0, False, True, True, True)
    pdbmod["extraParams"]= [
        extra_param_creator("Scale", 1.0, False, False, False, 0.0, 0.0, False, 12),
        extra_param_creator("Solvent ED", 334.0),
        extra_param_creator("C1", 1.0, False, True, True, 0.95, 1.05),
        extra_param_creator("Solvent Voxel Size", 0.2),
        extra_param_creator("Solvent Probe Radius", 0.14),
        extra_param_creator("Solvation Thickness", 0.28, False, True, True, 0.0),
        extra_param_creator("Outer Solvent ED"),
        extra_param_creator("Fill Holes", 0.0, False, False, True, 0.0, 1.0, True),
        extra_param_creator("Solvent Only", 0.0, False, False, True, 0.0, 1.0, True),
        extra_param_creator("Solvent method", 4.0, False, False, True, 0.0, 4.0, True)
    ]
    return pdbmod


def ampmodel():
    amp=create_hard_model("AMP", -1, 1000, False, 0, 0, 0, 1, 0, False, False, False, True)
    amp["extraParams"]= [
        extra_param_creator("Scale", 1.0, False, False, False, 0.0, 0.0, False, 12)
    ]
    return amp


def scriptedsymm():
    s_symm=create_hard_model("Scripted Symmetry", 9, 1003)
    return s_symm

def scriptedmodel():
    raise NotImplemented
def scriptedgeometry():
    raise NotImplemented



hardcode_models=[
    pdbmodel(),
    ampmodel(),
    #scriptedsymm()
]


program_metadata = [
    {
        "containerName": "xplusmodels",
        "models": [
            {
                "index": 0,
                "name": "Uniform Hollow Cylinder",
                "category": 0,
                "gpuCompatible": False,
                "slow": False,
                "ffImplemented": True,
                "isLayerBased": True,
                "layers": {
                    "min": 2,
                    "max": -1,
                    "layerInfo": [
                        {
                            "index": 0,
                            "name": "Solvent",
                            "applicability": [
                                1,
                                1
                            ],
                            "defaultValues": [
                                0,
                                333
                            ]
                        },
                        {
                            "index": 1,
                            "name": "Layer %d",
                            "applicability": [
                                1,
                                1
                            ],
                            "defaultValues": [
                                1,
                                400
                            ]
                        },
                        {
                            "index": -1,
                            "name": "Layer %d",
                            "applicability": [
                                1,
                                1
                            ],
                            "defaultValues": [
                                1,
                                400
                            ]
                        }
                    ],
                    "params": [
                        "Radius",
                        "E.D."
                    ]
                },
                "extraParams": [
                    {
                        "name": "Scale",
                        "defaultValue": 1,
                        "isIntegral": False,
                        "decimalPoints": 12,
                        "isAbsolute": False,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Background",
                        "defaultValue": 5,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": False,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Height",
                        "defaultValue": 10,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": True,
                        "canBeInfinite": True
                    }
                ]
            },
            {
                "index": 1,
                "name": "Cylindroid with Constant Eccentricity",
                "category": 4,
                "gpuCompatible": False,
                "slow": True,
                "ffImplemented": False,
                "isLayerBased": True,
                "layers": {
                    "min": 2,
                    "max": -1,
                    "layerInfo": [
                        {
                            "index": 0,
                            "name": "Solvent",
                            "applicability": [
                                1,
                                1
                            ],
                            "defaultValues": [
                                0,
                                333
                            ]
                        },
                        {
                            "index": 1,
                            "name": "Layer %d",
                            "applicability": [
                                1,
                                1
                            ],
                            "defaultValues": [
                                1,
                                400
                            ]
                        },
                        {
                            "index": -1,
                            "name": "Layer %d",
                            "applicability": [
                                1,
                                1
                            ],
                            "defaultValues": [
                                1,
                                400
                            ]
                        }
                    ],
                    "params": [
                        "Radius",
                        "E.D."
                    ]
                },
                "extraParams": [
                    {
                        "name": "Scale",
                        "defaultValue": 1,
                        "isIntegral": False,
                        "decimalPoints": 12,
                        "isAbsolute": False,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Background",
                        "defaultValue": 5,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": False,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Height",
                        "defaultValue": math.inf,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": True,
                        "canBeInfinite": True
                    },
                    {
                        "name": "Short inner radius",
                        "defaultValue": 1,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": True,
                        "canBeInfinite": False
                    }
                ]
            },
            {
                "index": 2,
                "name": "Sphere",
                "category": 1,
                "gpuCompatible": False,
                "slow": False,
                "ffImplemented": True,
                "isLayerBased": True,
                "layers": {
                    "min": 2,
                    "max": -1,
                    "layerInfo": [
                        {
                            "index": 0,
                            "name": "Solvent",
                            "applicability": [
                                1,
                                1
                            ],
                            "defaultValues": [
                                0,
                                333
                            ]
                        },
                        {
                            "index": 1,
                            "name": "Layer %d",
                            "applicability": [
                                1,
                                1
                            ],
                            "defaultValues": [
                                1,
                                400
                            ]
                        },
                        {
                            "index": -1,
                            "name": "Layer %d",
                            "applicability": [
                                1,
                                1
                            ],
                            "defaultValues": [
                                1,
                                400
                            ]
                        }
                    ],
                    "params": [
                        "Radius",
                        "E.D."
                    ]
                },
                "extraParams": [
                    {
                        "name": "Scale",
                        "defaultValue": 1,
                        "isIntegral": False,
                        "decimalPoints": 12,
                        "isAbsolute": False,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Background",
                        "defaultValue": 5,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": False,
                        "canBeInfinite": False
                    }
                ]
            },
            {
                "index": 3,
                "name": "Cuboid",
                "category": 6,
                "gpuCompatible": False,
                "slow": True,
                "ffImplemented": False,
                "isLayerBased": False,
                "layers": {
                    "min": 4,
                    "max": 4,
                    "layerInfo": [
                        {
                            "index": 0,
                            "name": "Contrast",
                            "applicability": [
                                0,
                                1
                            ],
                            "defaultValues": [
                                1,
                                333
                            ]
                        },
                        {
                            "index": 1,
                            "name": "Width",
                            "applicability": [
                                1,
                                0
                            ],
                            "defaultValues": [
                                1,
                                333
                            ]
                        },
                        {
                            "index": 2,
                            "name": "Height",
                            "applicability": [
                                1,
                                0
                            ],
                            "defaultValues": [
                                1,
                                333
                            ]
                        },
                        {
                            "index": 3,
                            "name": "Depth",
                            "applicability": [
                                1,
                                0
                            ],
                            "defaultValues": [
                                1,
                                333
                            ]
                        }
                    ],
                    "params": [
                        "Thickness",
                        "E.D."
                    ]
                },
                "extraParams": [
                    {
                        "name": "Scale",
                        "defaultValue": 1,
                        "isIntegral": False,
                        "decimalPoints": 12,
                        "isAbsolute": False,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Background",
                        "defaultValue": 5,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": False,
                        "canBeInfinite": False
                    }
                ]
            },
            {
                "index": 4,
                "name": "Symmetric Layered Slabs",
                "category": 2,
                "gpuCompatible": False,
                "slow": False,
                "ffImplemented": True,
                "isLayerBased": True,
                "layers": {
                    "min": 2,
                    "max": -1,
                    "layerInfo": [
                        {
                            "index": 0,
                            "name": "Solvent",
                            "applicability": [
                                0,
                                1
                            ],
                            "defaultValues": [
                                0,
                                333
                            ]
                        },
                        {
                            "index": 1,
                            "name": "Layer %d",
                            "applicability": [
                                1,
                                1
                            ],
                            "defaultValues": [
                                1,
                                280
                            ]
                        },
                        {
                            "index": -1,
                            "name": "Layer %d",
                            "applicability": [
                                1,
                                1
                            ],
                            "defaultValues": [
                                1,
                                400
                            ]
                        }
                    ],
                    "params": [
                        "Width",
                        "E.D."
                    ]
                },
                "extraParams": [
                    {
                        "name": "Scale",
                        "defaultValue": 1,
                        "isIntegral": False,
                        "decimalPoints": 12,
                        "isAbsolute": False,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Background",
                        "defaultValue": 5,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": False,
                        "canBeInfinite": False
                    },
                    {
                        "name": "X Domain Size",
                        "defaultValue": 10,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": True,
                        "canBeInfinite": True
                    },
                    {
                        "name": "Y Domain Size",
                        "defaultValue": 10,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": True,
                        "canBeInfinite": True
                    }
                ]
            },
            {
                "index": 5,
                "name": "Asymmetric Layered Slabs",
                "category": 2,
                "gpuCompatible": False,
                "slow": False,
                "ffImplemented": True,
                "isLayerBased": True,
                "layers": {
                    "min": 2,
                    "max": -1,
                    "layerInfo": [
                        {
                            "index": 0,
                            "name": "Solvent",
                            "applicability": [
                                0,
                                1
                            ],
                            "defaultValues": [
                                0,
                                333
                            ]
                        },
                        {
                            "index": 1,
                            "name": "Layer %d",
                            "applicability": [
                                1,
                                1
                            ],
                            "defaultValues": [
                                1,
                                280
                            ]
                        },
                        {
                            "index": -1,
                            "name": "Layer %d",
                            "applicability": [
                                1,
                                1
                            ],
                            "defaultValues": [
                                1,
                                400
                            ]
                        }
                    ],
                    "params": [
                        "Width",
                        "E.D."
                    ]
                },
                "extraParams": [
                    {
                        "name": "Scale",
                        "defaultValue": 1,
                        "isIntegral": False,
                        "decimalPoints": 12,
                        "isAbsolute": False,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Background",
                        "defaultValue": 5,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": False,
                        "canBeInfinite": False
                    },
                    {
                        "name": "X Domain Size",
                        "defaultValue": 10,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": True,
                        "canBeInfinite": True
                    },
                    {
                        "name": "Y Domain Size",
                        "defaultValue": 10,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": True,
                        "canBeInfinite": True
                    }
                ]
            },
            {
                "index": 6,
                "name": "Helix",
                "category": 3,
                "gpuCompatible": False,
                "slow": False,
                "ffImplemented": True,
                "isLayerBased": False,
                "layers": {
                    "min": 2,
                    "max": -1,
                    "layerInfo": [
                        {
                            "index": 0,
                            "name": "Solvent",
                            "applicability": [
                                0,
                                1,
                                0
                            ],
                            "defaultValues": [
                                0,
                                333,
                                0
                            ]
                        },
                        {
                            "index": 1,
                            "name": "Helix %d",
                            "applicability": [
                                0,
                                1,
                                1
                            ],
                            "defaultValues": [
                                0,
                                400,
                                3
                            ]
                        },
                        {
                            "index": -1,
                            "name": "Helix %d",
                            "applicability": [
                                1,
                                1,
                                1
                            ],
                            "defaultValues": [
                                1,
                                400,
                                3
                            ]
                        }
                    ],
                    "params": [
                        "Phase",
                        "E.D.",
                        "Cross Section"
                    ]
                },
                "extraParams": [
                    {
                        "name": "Scale",
                        "defaultValue": 1,
                        "isIntegral": False,
                        "decimalPoints": 12,
                        "isAbsolute": False,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Background",
                        "defaultValue": 5,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": False,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Height",
                        "defaultValue": math.inf,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": True,
                        "canBeInfinite": True
                    },
                    {
                        "name": "Helix Radius",
                        "defaultValue": 10,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": True,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Pitch",
                        "defaultValue": 15,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": True,
                        "canBeInfinite": False
                    }
                ]
            },
            {
                "index": 7,
                "name": "Discrete Helix",
                "category": 3,
                "gpuCompatible": False,
                "slow": True,
                "ffImplemented": True,
                "isLayerBased": False,
                "layers": {
                    "min": 2,
                    "max": -1,
                    "layerInfo": [
                        {
                            "index": 0,
                            "name": "Solvent",
                            "applicability": [
                                0,
                                1,
                                0
                            ],
                            "defaultValues": [
                                0,
                                333,
                                0
                            ]
                        },
                        {
                            "index": 1,
                            "name": "Helix %d",
                            "applicability": [
                                0,
                                1,
                                1
                            ],
                            "defaultValues": [
                                0,
                                400,
                                3
                            ]
                        },
                        {
                            "index": -1,
                            "name": "Helix %d",
                            "applicability": [
                                1,
                                1,
                                1
                            ],
                            "defaultValues": [
                                1,
                                400,
                                3
                            ]
                        }
                    ],
                    "params": [
                        "Phase",
                        "E.D.",
                        "Cross Section"
                    ]
                },
                "extraParams": [
                    {
                        "name": "Scale",
                        "defaultValue": 1,
                        "isIntegral": False,
                        "decimalPoints": 12,
                        "isAbsolute": False,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Background",
                        "defaultValue": 5,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": False,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Number of Spheres",
                        "defaultValue": 100,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": True,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Helix Radius",
                        "defaultValue": 10,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": True,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Pitch",
                        "defaultValue": 15,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": True,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Water Spacing",
                        "defaultValue": 0,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": True,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Debye Waller",
                        "defaultValue": 0,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": True,
                        "canBeInfinite": False
                    }
                ]
            },
            {
                "index": 8,
                "name": "Gaussian Slabs",
                "category": 2,
                "gpuCompatible": False,
                "slow": False,
                "ffImplemented": False,
                "isLayerBased": False,
                "layers": {
                    "min": 2,
                    "max": -1,
                    "layerInfo": [
                        {
                            "index": 0,
                            "name": "Solvent",
                            "applicability": [
                                0,
                                1,
                                0
                            ],
                            "defaultValues": [
                                0,
                                333,
                                0
                            ]
                        },
                        {
                            "index": 1,
                            "name": "Layer %d",
                            "applicability": [
                                1,
                                1,
                                0
                            ],
                            "defaultValues": [
                                1,
                                280,
                                0
                            ]
                        },
                        {
                            "index": -1,
                            "name": "Layer %d",
                            "applicability": [
                                1,
                                1,
                                1
                            ],
                            "defaultValues": [
                                1,
                                400,
                                1
                            ]
                        }
                    ],
                    "params": [
                        "Width",
                        "E.D.",
                        "Position"
                    ]
                },
                "extraParams": [
                    {
                        "name": "Scale",
                        "defaultValue": 1,
                        "isIntegral": False,
                        "decimalPoints": 12,
                        "isAbsolute": False,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Background",
                        "defaultValue": 5,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": False,
                        "canBeInfinite": False
                    }
                ]
            },
            {
                "index": 9,
                "name": "Membrane",
                "category": 2,
                "gpuCompatible": False,
                "slow": False,
                "ffImplemented": False,
                "isLayerBased": True,
                "layers": {
                    "min": 3,
                    "max": 3,
                    "layerInfo": [
                        {
                            "index": 0,
                            "name": "Solvent",
                            "applicability": [
                                0,
                                1,
                                0
                            ],
                            "defaultValues": [
                                0,
                                333,
                                0
                            ]
                        },
                        {
                            "index": 1,
                            "name": "Tail",
                            "applicability": [
                                1,
                                1,
                                0
                            ],
                            "defaultValues": [
                                1,
                                280,
                                0
                            ]
                        },
                        {
                            "index": 2,
                            "name": "Head",
                            "applicability": [
                                1,
                                1,
                                1
                            ],
                            "defaultValues": [
                                1,
                                400,
                                1
                            ]
                        }
                    ],
                    "params": [
                        "Width",
                        "E.D.",
                        "Position"
                    ]
                },
                "extraParams": [
                    {
                        "name": "Scale",
                        "defaultValue": 1,
                        "isIntegral": False,
                        "decimalPoints": 12,
                        "isAbsolute": False,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Background",
                        "defaultValue": 5,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": False,
                        "canBeInfinite": False
                    }
                ]
            },
            {
                "index": 10,
                "name": "Gaussian Sphere",
                "category": 1,
                "gpuCompatible": False,
                "slow": False,
                "ffImplemented": False,
                "isLayerBased": False,
                "layers": {
                    "min": 2,
                    "max": -1,
                    "layerInfo": [
                        {
                            "index": 0,
                            "name": "Solvent",
                            "applicability": [
                                0,
                                1
                            ],
                            "defaultValues": [
                                0,
                                333
                            ]
                        },
                        {
                            "index": 1,
                            "name": "Layer %d",
                            "applicability": [
                                1,
                                1
                            ],
                            "defaultValues": [
                                1,
                                400
                            ]
                        },
                        {
                            "index": -1,
                            "name": "Layer %d",
                            "applicability": [
                                1,
                                1
                            ],
                            "defaultValues": [
                                1,
                                400
                            ]
                        }
                    ],
                    "params": [
                        "Radius",
                        "E.D."
                    ]
                },
                "extraParams": [
                    {
                        "name": "Scale",
                        "defaultValue": 1,
                        "isIntegral": False,
                        "decimalPoints": 12,
                        "isAbsolute": False,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Background",
                        "defaultValue": 5,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": False,
                        "canBeInfinite": False
                    }
                ]
            },
            {
                "index": 11,
                "name": "Gaussian Hollow Cylinder",
                "category": 0,
                "gpuCompatible": False,
                "slow": False,
                "ffImplemented": True,
                "isLayerBased": False,
                "layers": {
                    "min": 2,
                    "max": -1,
                    "layerInfo": [
                        {
                            "index": 0,
                            "name": "Solvent",
                            "applicability": [
                                0,
                                1,
                                0
                            ],
                            "defaultValues": [
                                0,
                                333,
                                0
                            ]
                        },
                        {
                            "index": 1,
                            "name": "Layer %d",
                            "applicability": [
                                1,
                                1,
                                1
                            ],
                            "defaultValues": [
                                1,
                                400,
                                1
                            ]
                        },
                        {
                            "index": -1,
                            "name": "Layer %d",
                            "applicability": [
                                1,
                                1,
                                1
                            ],
                            "defaultValues": [
                                1,
                                400,
                                1
                            ]
                        }
                    ],
                    "params": [
                        "Thickness",
                        "E.D.",
                        "Z_0"
                    ]
                },
                "extraParams": [
                    {
                        "name": "Scale",
                        "defaultValue": 1,
                        "isIntegral": False,
                        "decimalPoints": 12,
                        "isAbsolute": False,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Background",
                        "defaultValue": 5,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": False,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Height",
                        "defaultValue": 10,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": True,
                        "canBeInfinite": True
                    }
                ]
            },
            {
                "index": 12,
                "name": "Smooth Sphere",
                "category": 1,
                "gpuCompatible": False,
                "slow": False,
                "ffImplemented": False,
                "isLayerBased": False,
                "layers": {
                    "min": 2,
                    "max": -1,
                    "layerInfo": [
                        {
                            "index": 0,
                            "name": "Solvent",
                            "applicability": [
                                1,
                                1,
                                1
                            ],
                            "defaultValues": [
                                0,
                                333,
                                1
                            ]
                        },
                        {
                            "index": 1,
                            "name": "Layer %d",
                            "applicability": [
                                1,
                                1,
                                1
                            ],
                            "defaultValues": [
                                1,
                                400,
                                1
                            ]
                        },
                        {
                            "index": -1,
                            "name": "Layer %d",
                            "applicability": [
                                1,
                                1,
                                1
                            ],
                            "defaultValues": [
                                2,
                                400,
                                1
                            ]
                        }
                    ],
                    "params": [
                        "Width",
                        "E.D.",
                        "Slope"
                    ]
                },
                "extraParams": [
                    {
                        "name": "Scale",
                        "defaultValue": 1,
                        "isIntegral": False,
                        "decimalPoints": 12,
                        "isAbsolute": False,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Background",
                        "defaultValue": 5,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": False,
                        "canBeInfinite": False
                    }
                ]
            },
            {
                "index": 13,
                "name": "Microemulsion",
                "category": 5,
                "gpuCompatible": False,
                "slow": False,
                "ffImplemented": False,
                "isLayerBased": False,
                "layers": {
                    "min": 0,
                    "max": 0,
                    "layerInfo": [],
                    "params": []
                },
                "extraParams": [
                    {
                        "name": "Scale",
                        "defaultValue": 1,
                        "isIntegral": False,
                        "decimalPoints": 12,
                        "isAbsolute": False,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Background",
                        "defaultValue": 5,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": False,
                        "canBeInfinite": False
                    },
                    {
                        "name": "I(0)",
                        "defaultValue": 10,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": True,
                        "canBeInfinite": False
                    },
                    {
                        "name": "I(max)",
                        "defaultValue": 20,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": True,
                        "canBeInfinite": False
                    },
                    {
                        "name": "q(max)",
                        "defaultValue": 1,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": True,
                        "canBeInfinite": False
                    }
                ]
            },
            {
                "index": 14,
                "name": "Gaussian Hollow Cylinder with Hexagonal Structure Factor",
                "category": 0,
                "gpuCompatible": False,
                "slow": True,
                "ffImplemented": False,
                "isLayerBased": False,
                "layers": {
                    "min": 2,
                    "max": -1,
                    "layerInfo": [
                        {
                            "index": 0,
                            "name": "Solvent",
                            "applicability": [
                                0,
                                1,
                                0
                            ],
                            "defaultValues": [
                                0,
                                333,
                                0
                            ]
                        },
                        {
                            "index": 1,
                            "name": "Layer %d",
                            "applicability": [
                                1,
                                1,
                                1
                            ],
                            "defaultValues": [
                                1,
                                400,
                                1
                            ]
                        },
                        {
                            "index": -1,
                            "name": "Layer %d",
                            "applicability": [
                                1,
                                1,
                                1
                            ],
                            "defaultValues": [
                                1,
                                400,
                                1
                            ]
                        }
                    ],
                    "params": [
                        "Thickness",
                        "E.D.",
                        "Z_0"
                    ]
                },
                "extraParams": [
                    {
                        "name": "Scale",
                        "defaultValue": 1,
                        "isIntegral": False,
                        "decimalPoints": 12,
                        "isAbsolute": False,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Background",
                        "defaultValue": 5,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": False,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Height",
                        "defaultValue": 10,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": True,
                        "canBeInfinite": True
                    },
                    {
                        "name": "SF Scale",
                        "defaultValue": 1,
                        "isIntegral": False,
                        "decimalPoints": 12,
                        "isAbsolute": True,
                        "canBeInfinite": False
                    },
                    {
                        "name": "SF Background",
                        "defaultValue": 0.1,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": False,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Lf",
                        "defaultValue": 200,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": True,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Lattice Spacing",
                        "defaultValue": 25,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": True,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Debye-Waller",
                        "defaultValue": 0,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": True,
                        "canBeInfinite": False
                    }
                ]
            },
            {
                "index": 15,
                "name": "Uniform Hollow Cylinder with Hexagonal Structure Factor",
                "category": 0,
                "gpuCompatible": False,
                "slow": True,
                "ffImplemented": False,
                "isLayerBased": False,
                "layers": {
                    "min": 2,
                    "max": -1,
                    "layerInfo": [
                        {
                            "index": 0,
                            "name": "Solvent",
                            "applicability": [
                                1,
                                1
                            ],
                            "defaultValues": [
                                0,
                                333
                            ]
                        },
                        {
                            "index": 1,
                            "name": "Layer %d",
                            "applicability": [
                                1,
                                1
                            ],
                            "defaultValues": [
                                1,
                                400
                            ]
                        },
                        {
                            "index": -1,
                            "name": "Layer %d",
                            "applicability": [
                                1,
                                1
                            ],
                            "defaultValues": [
                                1,
                                400
                            ]
                        }
                    ],
                    "params": [
                        "Radius",
                        "E.D."
                    ]
                },
                "extraParams": [
                    {
                        "name": "Scale",
                        "defaultValue": 1,
                        "isIntegral": False,
                        "decimalPoints": 12,
                        "isAbsolute": False,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Background",
                        "defaultValue": 5,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": False,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Height",
                        "defaultValue": 10,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": True,
                        "canBeInfinite": True
                    },
                    {
                        "name": "SF Scale",
                        "defaultValue": 1,
                        "isIntegral": False,
                        "decimalPoints": 12,
                        "isAbsolute": True,
                        "canBeInfinite": False
                    },
                    {
                        "name": "SF Background",
                        "defaultValue": 0.1,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": False,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Lf",
                        "defaultValue": 200,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": True,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Lattice Spacing",
                        "defaultValue": 25,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": True,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Debye-Waller",
                        "defaultValue": 0,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": True,
                        "canBeInfinite": False
                    }
                ]
            },
            {
                "index": 16,
                "name": "Helix with Hexagonal Structure Factor",
                "category": 3,
                "gpuCompatible": False,
                "slow": True,
                "ffImplemented": False,
                "isLayerBased": False,
                "layers": {
                    "min": 2,
                    "max": -1,
                    "layerInfo": [
                        {
                            "index": 0,
                            "name": "Solvent",
                            "applicability": [
                                0,
                                1,
                                0
                            ],
                            "defaultValues": [
                                0,
                                333,
                                0
                            ]
                        },
                        {
                            "index": 1,
                            "name": "Helix %d",
                            "applicability": [
                                0,
                                1,
                                1
                            ],
                            "defaultValues": [
                                0,
                                400,
                                3
                            ]
                        },
                        {
                            "index": -1,
                            "name": "Helix %d",
                            "applicability": [
                                1,
                                1,
                                1
                            ],
                            "defaultValues": [
                                1,
                                400,
                                3
                            ]
                        }
                    ],
                    "params": [
                        "Phase",
                        "E.D.",
                        "Cross Section"
                    ]
                },
                "extraParams": [
                    {
                        "name": "Scale",
                        "defaultValue": 1,
                        "isIntegral": False,
                        "decimalPoints": 12,
                        "isAbsolute": False,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Background",
                        "defaultValue": 5,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": False,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Height",
                        "defaultValue": math.inf,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": True,
                        "canBeInfinite": True
                    },
                    {
                        "name": "Helix Radius",
                        "defaultValue": 10,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": True,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Pitch",
                        "defaultValue": 15,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": True,
                        "canBeInfinite": False
                    },
                    {
                        "name": "SF Scale",
                        "defaultValue": 1,
                        "isIntegral": False,
                        "decimalPoints": 12,
                        "isAbsolute": True,
                        "canBeInfinite": False
                    },
                    {
                        "name": "SF Background",
                        "defaultValue": 0.1,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": False,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Lf",
                        "defaultValue": 200,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": True,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Lattice Spacing",
                        "defaultValue": 25,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": True,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Debye-Waller",
                        "defaultValue": 0,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": True,
                        "canBeInfinite": False
                    }
                ]
            },
            {
                "index": 17,
                "name": "Gaussian Discrete Helix",
                "category": 3,
                "gpuCompatible": False,
                "slow": True,
                "ffImplemented": False,
                "isLayerBased": False,
                "layers": {
                    "min": 2,
                    "max": -1,
                    "layerInfo": [
                        {
                            "index": 0,
                            "name": "Solvent",
                            "applicability": [
                                0,
                                1,
                                0
                            ],
                            "defaultValues": [
                                0,
                                333,
                                0
                            ]
                        },
                        {
                            "index": 1,
                            "name": "Helix %d",
                            "applicability": [
                                0,
                                1,
                                1
                            ],
                            "defaultValues": [
                                0,
                                400,
                                3
                            ]
                        },
                        {
                            "index": -1,
                            "name": "Helix %d",
                            "applicability": [
                                1,
                                1,
                                1
                            ],
                            "defaultValues": [
                                1,
                                400,
                                3
                            ]
                        }
                    ],
                    "params": [
                        "Phase",
                        "E.D.",
                        "Cross Section"
                    ]
                },
                "extraParams": [
                    {
                        "name": "Scale",
                        "defaultValue": 1,
                        "isIntegral": False,
                        "decimalPoints": 12,
                        "isAbsolute": False,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Background",
                        "defaultValue": 5,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": False,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Number of Spheres",
                        "defaultValue": 100,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": True,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Helix Radius",
                        "defaultValue": 10,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": True,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Pitch",
                        "defaultValue": 15,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": True,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Water Spacing",
                        "defaultValue": 0,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": True,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Debye Waller",
                        "defaultValue": 0,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": True,
                        "canBeInfinite": False
                    }
                ]
            },
            {
                "index": 18,
                "name": "Cylindroid with Variable Eccentricity",
                "category": 4,
                "gpuCompatible": False,
                "slow": True,
                "ffImplemented": False,
                "isLayerBased": False,
                "layers": {
                    "min": 2,
                    "max": -1,
                    "layerInfo": [
                        {
                            "index": 0,
                            "name": "Solvent",
                            "applicability": [
                                1,
                                1
                            ],
                            "defaultValues": [
                                0,
                                333
                            ]
                        },
                        {
                            "index": 1,
                            "name": "Layer %d",
                            "applicability": [
                                1,
                                1
                            ],
                            "defaultValues": [
                                1,
                                400
                            ]
                        },
                        {
                            "index": -1,
                            "name": "Layer %d",
                            "applicability": [
                                1,
                                1
                            ],
                            "defaultValues": [
                                1,
                                400
                            ]
                        }
                    ],
                    "params": [
                        "Radius",
                        "E.D."
                    ]
                },
                "extraParams": [
                    {
                        "name": "Scale",
                        "defaultValue": 1,
                        "isIntegral": False,
                        "decimalPoints": 12,
                        "isAbsolute": False,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Background",
                        "defaultValue": 5,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": False,
                        "canBeInfinite": False
                    },
                    {
                        "name": "Height",
                        "defaultValue": math.inf,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": True,
                        "canBeInfinite": True
                    },
                    {
                        "name": "Short inner radius",
                        "defaultValue": 1,
                        "isIntegral": False,
                        "decimalPoints": 6,
                        "isAbsolute": True,
                        "canBeInfinite": False
                    }
                ]
            },
            {
                "index": 19,
                "name": "Gaussian Sigma Peak Model",
                "category": 7,
                "gpuCompatible": False,
                "slow": False,
                "ffImplemented": False,
                "isLayerBased": True
            },
            {
                "index": 20,
                "name": "Lorentzian Peak Model",
                "category": 7,
                "gpuCompatible": False,
                "slow": False,
                "ffImplemented": False,
                "isLayerBased": True
            },
            {
                "index": 21,
                "name": "Lorentzian Squared Peak Model",
                "category": 7,
                "gpuCompatible": False,
                "slow": False,
                "ffImplemented": False,
                "isLayerBased": True
            },
            {
                "index": 22,
                "name": "Caille Structure Factor",
                "category": 7,
                "gpuCompatible": False,
                "slow": False,
                "ffImplemented": False,
                "isLayerBased": False,
                "layers": {
                    "min": 1,
                    "max": 1,
                    "layerInfo": [
                        {
                            "index": 0,
                            "name": "Solvent",
                            "applicability": [
                                1,
                                1,
                                1,
                                1,
                                1,
                                1
                            ],
                            "defaultValues": [
                                1,
                                1,
                                0.05,
                                20,
                                2,
                                0
                            ]
                        }
                    ],
                    "params": [
                        "D",
                        "Amplitude",
                        "Eta",
                        "N0",
                        "Sigma",
                        "NDiff"
                    ]
                }
            },
            {
                "index": 23,
                "name": "Additive Background Functions",
                "category": 8,
                "gpuCompatible": False,
                "slow": False,
                "ffImplemented": False,
                "isLayerBased": True
            },
            {
                "index": 24,
                "name": "Mixed Peak SF Model",
                "category": 7,
                "gpuCompatible": False,
                "slow": False,
                "ffImplemented": False,
                "isLayerBased": True
            },
            {
                "index": 25,
                "name": "Space-filling Symmetry",
                "category": 9,
                "gpuCompatible": False,
                "slow": False,
                "ffImplemented": False,
                "isLayerBased": True,
                "layers": {
                    "min": 3,
                    "max": 3,
                    "layerInfo": [
                        {
                            "index": 0,
                            "name": "Vector 1",
                            "applicability": [
                                1,
                                1,
                                1
                            ],
                            "defaultValues": [
                                2.5,
                                90,
                                2
                            ]
                        },
                        {
                            "index": 1,
                            "name": "Vector 2",
                            "applicability": [
                                1,
                                1,
                                1
                            ],
                            "defaultValues": [
                                2.5,
                                90,
                                2
                            ]
                        },
                        {
                            "index": 2,
                            "name": "Vector 3",
                            "applicability": [
                                1,
                                1,
                                1
                            ],
                            "defaultValues": [
                                2.5,
                                90,
                                2
                            ]
                        }
                    ],
                    "params": [
                        "Distance",
                        "Angle",
                        "Repetitions"
                    ]
                },
                "extraParams": [
                    {
                        "name": "Scale",
                        "defaultValue": 1,
                        "isIntegral": False,
                        "decimalPoints": 12,
                        "isAbsolute": True,
                        "canBeInfinite": False
                    }
                ]
            },
            {
                "index": 26,
                "name": "Manual Symmetry",
                "category": 9,
                "gpuCompatible": False,
                "slow": False,
                "ffImplemented": False,
                "isLayerBased": True,
                "layers": {
                    "min": 0,
                    "max": -1,
                    "layerInfo": [
                        {
                            "index": -1,
                            "name": "Instance %d",
                            "applicability": [
                                1,
                                1,
                                1,
                                1,
                                1,
                                1
                            ],
                            "defaultValues": [
                                0,
                                0,
                                0,
                                0,
                                0,
                                0
                            ]
                        }
                    ],
                    "params": [
                        "X",
                        "Y",
                        "Z",
                        "Alpha",
                        "Beta",
                        "Gamma"
                    ]
                },
                "extraParams": [
                    {
                        "name": "Scale",
                        "defaultValue": 1,
                        "range": {
                            "min": 0,
                            "max": 0
                        },
                        "isIntegral": False,
                        "decimalPoints": 12,
                        "isAbsolute": True,
                        "canBeInfinite": False
                    }
                ]
            }
        ],
        "modelCategories": [
            {
                "name": "Cylindrical Models",
                "index": 0,
                "type": 1,
                "models": [
                    0,
                    11,
                    14,
                    15
                ]
            },
            {
                "name": "Spherical Models",
                "index": 1,
                "type": 1,
                "models": [
                    2,
                    10,
                    12
                ]
            },
            {
                "name": "Slab Models",
                "index": 2,
                "type": 1,
                "models": [
                    4,
                    5,
                    8,
                    9
                ]
            },
            {
                "name": "Helical Models",
                "index": 3,
                "type": 1,
                "models": [
                    6,
                    7,
                    16,
                    17
                ]
            },
            {
                "name": "Cylindroids",
                "index": 4,
                "type": 1,
                "models": [
                    1,
                    18
                ]
            },
            {
                "name": "Microemulsions",
                "index": 5,
                "type": 1,
                "models": [
                    13
                ]
            },
            {
                "name": "Cuboids",
                "index": 6,
                "type": 1,
                "models": [
                    3
                ]
            },
            {
                "name": "Structure Factors",
                "index": 7,
                "type": 2,
                "models": [
                    19,
                    20,
                    21,
                    22,
                    24
                ]
            },
            {
                "name": "Backgrounds",
                "index": 8,
                "type": 4,
                "models": [
                    23
                ]
            },
            {
                "name": "Symmetries",
                "index": 9,
                "type": 8,
                "models": [
                    25,
                    26
                ]
            }
        ]
    }
]
meta_models = program_metadata[0]["models"]




#NOTES:


#	isIntegral(bInt), decimalPoints(decPoints), isRanged(bRange),
#		rangeMin(minval), rangeMax(maxval), isAbsolute(bAbs),
#		canBeInfinite(bInf), defaultVal(defval) {
#			if(bInt)
#				decimalPoints = 0;



'''
PDBModelUI::PDBModelUI(const char *tName) {
	mi.nExtraParams = 8;

	this->extraParamsInfo.resize(mi.nExtraParams);
	extraParamsInfo[0] = ExtraParam("Scale", 1.0, False, False, False, 0.0, 0.0, False, 12);
	extraParamsInfo[1] = ExtraParam("Solvent ED");
	extraParamsInfo[2] = ExtraParam("Solvent Voxel Size", 0.05);
	extraParamsInfo[3] = ExtraParam("Solvent Radius", 0.14);
	extraParamsInfo[4] = ExtraParam("Outer Solvent ED");
	extraParamsInfo[5] = ExtraParam("Fill Holes", 0.0, False, False, True, 0.0, 1.0, True);
	extraParamsInfo[6] = ExtraParam("Solvent Only", 0.0, False, False, True, 0.0, 1.0, True);
	extraParamsInfo[7] = ExtraParam("Solvent method", 0.0, False, False, True, 0.0, 4.0, True);

	extraParamsTypes.resize(mi.nExtraParams, EPT_DOUBLE);
	extraParamOptions.resize(mi.nExtraParams, std::vector<std::string>());

	extraParamsTypes[5] = EPT_CHECKBOX;
	extraParamsTypes[6] = EPT_CHECKBOX;
	extraParamsTypes[7] = EPT_MULTIPLE_CHOICE;

	extraParamOptions[7].resize(RAD_SIZE);
	extraParamOptions[7][0] = "No Solvent";
	extraParamOptions[7][1] = "Van der Waals";
	extraParamOptions[7][2] = "Empirical";
	extraParamOptions[7][3] = "Calculated";
	extraParamOptions[7][4] = "Dummy Atoms";

	mi = ModelInformation(tName, -1, -1, False, 0, 0, 0, 8, 0, False /*TODO::GPU*/, True, True, True/*even though this is never used*/);

}

	mi.nExtraParams = 1;

	this->extraParamsInfo.resize(mi.nExtraParams);
	extraParamsInfo[0] = ExtraParam("Scale", 1.0, False, False, False, 0.0, 0.0, False, 12);

	extraParamsTypes.resize(mi.nExtraParams, EPT_DOUBLE);
	extraParamOptions.resize(mi.nExtraParams, std::vector<std::string>());

	mi = ModelInformation(tName, -1, -1, False, 0, 0, 0, 1, 0, False /*TODO::GPU*/, False, False, True/*even though this is never used*/);
'''