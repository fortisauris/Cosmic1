import matplotlib.pyplot as mp

mp.figure(figsize=(5,5))
total_weight = ['ship - 106 197kg', 'Crew - 233kg', 'fuel - 7000kg']
weight = [106197,233,7000]
mp.pie(weight, labels=total_weight, shadow=False)
mp.title('TOTAL WEIGHT - 113 430kg')
mp.show()

