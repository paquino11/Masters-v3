


data = {
  "results": [
    {
      "invitation_mode": "once",
    },
        {
      "invitation_mode": "once",
    },
        {
      "invitation_mode": "once",
    }
  ]
}

n_results = len(data["results"])
print(n_results)
n_connections = 0
while True:
    n_results = len(data["results"])
    #print(n_results)
    if(n_connections<n_results):
        n_connections += 1
        print(n_connections)
        print(n_results)
        print("New Connection")
