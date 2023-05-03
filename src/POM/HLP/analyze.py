import grblogtools as glt
import matplotlib.pyplot as plt

summary = glt.parse("modelCutting.log").summary()
glt.plot(summary)
