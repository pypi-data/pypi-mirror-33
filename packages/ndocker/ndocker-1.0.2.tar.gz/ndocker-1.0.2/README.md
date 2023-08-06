# Docker network configration for UTE

Origin:

Docker networking is a boring job in our daily testing job.
We run many contaniers on one server and have to config several interfaces for each container and isolate IPs among them. and when container restarted, all networks are lost.

That's why we neet the project.