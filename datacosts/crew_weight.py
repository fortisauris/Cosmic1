import matplotlib.pyplot as mp

mp.figure(figsize=(5,5))
crew = ['Mike - 78kg', 'Carl - 80kg', 'Gordon - 75kg']
vaha = [78,80,75]
mp.pie(vaha, labels=crew, shadow=False)
mp.title('CREW weight - 233kg')
mp.show()