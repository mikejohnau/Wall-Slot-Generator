# Privacy Policy — Wall Slot Generator

**Publisher:** Michael Johnson, M2 Design  
**Effective date:** 24 September 2026  
**Contact:** michael@m2-design.net

---

## 1. Data collected, how it is collected, and how it is used

Wall Slot Generator collects and stores only the following preference values:

| Value | Description |
|---|---|
| Wall width, height, thickness | Numeric dimensions in mm |
| Border width | Numeric dimension in mm |
| Design type | Integer (1 or 2) |
| Packing density | Integer 0–100 |
| Half-ends setting | Boolean (on/off) |
| Subscription check | Autodesk user id, this app's id, and whether the check succeeded |

**How it is collected:** Panel values are written automatically when you click
Generate. They are stored as Autodesk Fusion 360 document attributes on your
local machine, using Fusion's built-in `design.attributes` API. They are not
sent to M2 Design.

Once each Fusion session, the add-in sends your Autodesk user id and the
Wall Slot Generator app id to Autodesk at `https://apps.autodesk.com/webservices/checkentitlement`.
Autodesk responds with whether your monthly or yearly subscription is active.
A successful check is saved in `entitlement_cache.json` next to the add-in for
up to 7 days so **Generate wall** can keep working offline. No wall dimensions
or design data are included in that request.

**How it is used:** Panel values pre-populate the panel the next time you open
the add-in in the same document. The entitlement response decides whether
**Generate wall** is available.

The add-in has no analytics, no telemetry, no crash reporting, and no advertising.

---

## 2. Third parties

Wall Slot Generator does not share data with analytics tools, advertising
networks, or affiliates. The only network request is the subscription check
sent to Autodesk's App Store entitlement service, described above. Autodesk's
own privacy policy covers that service.

---

## 3. Data retention and deletion

Preference values are stored as Fusion 360 document attributes and persist for
as long as the Fusion 360 document in which they were saved exists on your
machine. They are automatically removed if you delete the document.

If you wish to clear the stored preferences without deleting the document, you
can do so by using Fusion 360's built-in document attribute tools, or by
uninstalling the add-in and deleting the document attributes manually.

---

## 4. Revoking consent and requesting deletion

M2 Design does not receive or store any data from this add-in, so there is no
M2 Design account to delete. The subscription check is sent only to Autodesk,
which already holds the App Store account used to subscribe.

To remove all data stored by Wall Slot Generator on your local machine:

1. Open the Fusion 360 document in which you used the add-in
2. Go to **Tools → Scripts and Add-Ins → Add-Ins**, select Wall Slot Generator,
   and click **Stop**
3. Open the **Data Panel**, right-click the document, and choose
   **View Details on Web**, then use Autodesk's account data tools if desired
4. Alternatively, delete or close the Fusion 360 document — this removes all
   stored preferences associated with it

To uninstall the add-in entirely, remove the `wall_slots` folder from your
Fusion 360 AddIns directory. That removes the add-in and the local
`entitlement_cache.json` file.

For any privacy questions or requests, contact: [your contact email]

---

*This policy applies solely to the Wall Slot Generator add-in. It does not
apply to Autodesk Fusion 360 itself, which has its own privacy policy at
https://www.autodesk.com/company/legal-notices-trademarks/privacy-statement.*
