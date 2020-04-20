import finance

portfolio = finance.levelPrice(finance.evalPortfolio(finance.consolidateQuotes()))

import pandas as pd
benchmarks = pd.Series(['^GSPC', '^IXIC', '^DJI'])
    
import sys
print(sys.argv[1:])
df = finance.levelPrice(finance.combineAdjClose(benchmarks.append(pd.Series(sys.argv[1:]))))
df = df.join(portfolio, how='outer')

# Plot data frame
import matplotlib.pyplot as plt
from matplotlib import style
style.use('ggplot') 
df[-200:-1].plot()

plt.title('Stock Performance')
plt.ylabel('Scaled Price')
plt.xlabel('Trade Date')
plt.show()


