   ![SC2006 SCS4 GRP 60](https://github.com/user-attachments/assets/45797068-ed8d-492f-8f4a-eb4f0fe039c5)

NTU SC2006 Software Engineering Group Project

In alignment with Singapore’s Zero Waste Masterplan to reduce waste sent to landfills by 30% by 2030, we as a group have decided to create a convenient and intuitive website for users to find their most convenient recycling locations. Therefore, the project mission statement is “Recyclo empowers Singapore residents to locate the nearest recycling facilities that accept specific types of waste, addressing the challenge of finding accessible and suitable locations for responsible disposal. By streamlining this process, Recyclo supports Singapore’s green initiatives, reduces landfill waste, and encourages sustainable habits among residents for a cleaner environment.

## Team Members

We are from group 60 from lab group SCS4, there are 6 members in our group:

| Name              | Github Account                                           | Email                 |
|-------------------|----------------------------------------------------------|-----------------------|
| Park Yumin       | [YuminPark78](https://github.com/YuminPark78)            | [yumin002@e.ntu.edu.sg](mailto:yumin002@e.ntu.edu.sg) |
| Shen Jia Cheng    | [shenjc01](https://github.com/shenjc01)                  | [jshen010@e.ntu.edu.sg](mailto:jshen010@e.ntu.edu.sg) |
| Saravanan Deepika  | [DeepikaSaravanan5](https://github.com/DeepikaSaravanan5) | [deepika008@e.ntu.edu.sg](mailto:deepika008@e.ntu.edu.sg) |
| Ng Wei Yu         | [firepiratex](https://github.com/firepiratex)            | [wng081@e.ntu.edu.sg](mailto:wng081@e.ntu.edu.sg)  |
| Tay Jih How       | [JaredXwos](https://github.com/JaredXwos)                | [c220171@e.ntu.edu.sg](mailto:c220171@e.ntu.edu.sg)  |
| See Tow Tze Jiet  | [Paxton2001](https://github.com/Paxton2001)              | [seet0081@e.ntu.edu.sg](mailto:seet0081@e.ntu.edu.sg)  |

## Highlights

- **Location Search**: Look for the closest recycle location that accepts your waste.
- **Bookmarks**: Save your location for future references.
- **Comments**: Share your thoughts about the location to the community.

## Features

- [x] Login/Logout/Register
- [x] Guide
- [x] Feedback
- [x] Search Location
- [x] Bookmarks
- [x] Comments 

## Build

Download the project from GitHub or you can use git

```bash
git clone https://github.com/YuminPark78/2006swe60-1.git
```

Download [Go](https://go.dev/doc/install) in order to build and run the project

The project is built with Go.

Open Command Prompt(cmd) navigate to the project file path and run this command

```go build -o server.exe main.go```

This will create a server.exe file for you to start the server and running it will allow you to access the server by

```http://localhost:8080```

At any time during the server run, one may shut down the server by typing the ```#``` character into the cmd window running the project. This will consolidate all the database updates and gracefully close the servers.
