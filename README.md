Repository: https://github.com/fbtd4vrycv-dev/CapstoneNoShowGuard

# Capstone NoShowGuard

## Four-Part Summary

- **Part 1:** The cleaned appointment export contains **990 rows** and **16 columns**.
- **Part 2:** There are **218 no-shows among 990 appointments (22.0%)** across **8 clinics**; Gomti Nagar had the highest overall rate, **33.3% of 90 appointments**.
- **Part 3:** Logistic regression led training-only cross-validation (**ROC-AUC 0.774**); at threshold **0.35**, test ROC-AUC was **0.789**, recall was **0.571**, and **49 of 198** appointments were flagged.
- **Part 4:** Of **10** analyzed follow-up notes, **5** matched appointments with no reminder; both **2 of 2** notes classified as forgotten/no reminder had `reminder_sent = No`.

## Recommendation

Use logistic regression to rank appointments for follow-up: it had the highest training-only 5-fold cross-validated ROC-AUC (**0.774**, compared with **0.767** for the tuned forest). A threshold of **0.35**, selected from out-of-fold training predictions because its F1 was **0.489** versus **0.347** at 0.50, achieved test ROC-AUC **0.789** and recall **0.571**, flagging **49 of 198** test appointments. In the notes sample, **5 of 10** appointments had no reminder and both **2 of 2** forgotten/no-reminder cases had no reminder, so pilot contact-detail checks, reminder-delivery checks, and targeted follow-up calls; set the operating threshold to fit the front desk's evening call capacity and the cost of an empty slot. These reminder findings are associations in observational data, not evidence that reminders cause attendance.

## Limitations

- The **10** call-centre notes are illustrative and cannot establish clinic-wide reasons for missed appointments.
- Cleaning statistics were calculated from all rows before the train/test split, so preprocessing can reflect information from the test portion.
- The data are observational, so associations between reminders and no-shows do not establish cause and effect.
