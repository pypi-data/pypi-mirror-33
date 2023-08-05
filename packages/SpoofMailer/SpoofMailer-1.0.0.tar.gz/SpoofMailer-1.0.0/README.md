# SpoofMailer

This is a python pip module that is use for sending spoof mail without need to create any server. Or you can create your own email API.

## Step 1 :-

```
import SpoofMailer as sp
```

## Step 2 :-

```
sp.set_sender_name("Name")
```

## Step 3 :-

```
sp.set_sender_email("email@example.com")
```

## Step 4 :-

```
sp.set_receiver_email("receviver@example.com")
```

## Step 5 :-

```
sp.set_subject("Subject of the mail")
```

## Step 6 :-

```
sp.set_body("Body of the email")
```

## Final step

```
rq = sp.send()

if ( rq == 200 ):
    print("Mail sent!")
else:
    print("Error :"+rq)
```
Your mail was successfully sent!


Don't use this service for illegal purpose. **We are not responsible for your crimes**.

[@DipankerShah](https://www.facebook.com/dipankar.shah.5)
Contact me