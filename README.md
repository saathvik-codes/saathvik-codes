<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:0EA5E9,100:38BDF8&height=180&section=header&text=Saathvik%20Kalepu&fontSize=42&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=Backend%20Engineer%20%7C%20Distributed%20Systems&descAlignY=58&descSize=18" />
</p>

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=18&duration=3000&pause=1000&color=38BDF8&center=true&vCenter=true&width=600&lines=Wrote+a+Raft+consensus+engine+from+scratch+in+Go;Chaos-tested+it+by+killing+nodes+mid-traffic;Still+debugging+something+at+2am+probably" />
</p>

Hey, I'm Saathvik — I work backend at **Caterworld.ai** and spend my free time
building things that most people would just reach for a library for, because
I want to actually understand what's happening underneath. Most recently that
meant implementing Raft leader election and log replication by hand in Go,
then writing a harness that kills random nodes under load just to see if it
survives (it does — 17,658 writes, 0 failures, receipts in the repo).

I like backend systems that have to hold up under real conditions — multi-
tenant isolation that can't leak, rate limiters that can't be gamed, stores
that can't lose data on a crash. If it hasn't been tested against failure,
I don't consider it done.

- 🛠️ Right now: `QuorumDB` — a distributed KV store, built twice with two
  different replication strategies (quorum+LWW and Raft) so I could feel the
  actual tradeoff instead of reading about it
- 🧠 Java/Spring Boot by day, Go for systems-level stuff on the side
- 📫 saathvikk202@gmail.com

<p align="center">
  <a href="https://linkedin.com/in/saathvik-kalepu-17041228b/"><img src="https://img.shields.io/badge/LinkedIn-%230077B5.svg?logo=linkedin&logoColor=white" /></a>
  <a href="mailto:saathvikk202@gmail.com"><img src="https://img.shields.io/badge/Email-D14836?logo=gmail&logoColor=white" /></a>
  <a href="https://saathvik-kalepu.vercel.app/"><img src="https://img.shields.io/badge/Portfolio-000000?logo=vercel&logoColor=white" /></a>
</p>

### What I actually reach for
<p>
  <img src="https://img.shields.io/badge/java-%23ED8B00.svg?style=flat-square&logo=openjdk&logoColor=white" />
  <img src="https://img.shields.io/badge/go-%2300ADD8.svg?style=flat-square&logo=go&logoColor=white" />
  <img src="https://img.shields.io/badge/springboot-%236DB33F.svg?style=flat-square&logo=spring-boot&logoColor=white" />
  <img src="https://img.shields.io/badge/typescript-%23007ACC.svg?style=flat-square&logo=typescript&logoColor=white" />
  <img src="https://img.shields.io/badge/Next-black?style=flat-square&logo=next.js&logoColor=white" />
  <img src="https://img.shields.io/badge/postgresql-%23316192.svg?style=flat-square&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=flat-square&logo=mongodb&logoColor=white" />
  <img src="https://img.shields.io/badge/docker-%230db7ed.svg?style=flat-square&logo=docker&logoColor=white" />
</p>

### Projects worth actually looking at

**[QuorumDB](https://github.com/saathvik-codes/quorumdb)** — distributed KV store, two replication engines (quorum+LWW and a from-scratch Raft), LSM storage with bloom filters + compaction, chaos-tested under live node failures. *Go, zero dependencies.*

**[HiveCRM](https://github.com/saathvik-codes/hivecrm)** — multi-tenant SaaS CRM where tenant isolation is enforced at the repository layer, not just the API — verified a cross-tenant fetch actually 404s. *Spring Boot, PostgreSQL.*

**[TaskWave](https://github.com/saathvik-codes/taskwave)** — real-time collaborative Kanban boards, live activity feed over raw STOMP/WebSocket frames. *Spring Boot, Next.js.*

**[FraudShield](https://github.com/saathvik-codes/fraudshield)** — composable rules engine for transaction fraud (velocity checks, new-beneficiary flags, large-amount thresholds). *Spring Boot, MongoDB.*

**[GateKeeper](https://github.com/saathvik-codes/gatekeeper)** — API gateway: JWT + API-key auth, per-route RBAC, sliding-window rate limiting. *Spring Boot.*

<p align="center">
  <img src="https://github-readme-stats-sigma-eight.vercel.app/api?username=saathvik-codes&theme=tokyonight&hide_border=true&show_icons=true&include_all_commits=true&count_private=true" height="165"/>
  <img src="https://github-readme-stats-sigma-eight.vercel.app/api/top-langs/?username=saathvik-codes&theme=tokyonight&hide_border=true&layout=compact&include_all_commits=true&count_private=true" height="165"/>
</p>

<p align="center">
  <img src="https://github-readme-streak-stats.herokuapp.com/?user=saathvik-codes&theme=tokyonight&hide_border=true" />
</p>

<p align="center"><i>Building twice — once to make it work, once to make it survive.</i></p>
