# Privacy Policy — Wall Slot Generator

**Publisher:** Michael Johnson, M2 Design  
**Effective date:** 2 April 2026  
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

**How it is collected:** These values are written automatically when you click
Generate. They are stored exclusively as Autodesk Fusion 360 document attributes
on your local machine, using Fusion's built-in `design.attributes` API. No data
is transmitted over a network, sent to any server, or stored outside your local
Fusion 360 environment.

**How it is used:** The sole purpose of storing these values is to pre-populate
the panel the next time you open the add-in within the same Fusion 360 document,
so you do not need to re-enter dimensions for subsequent iterations.

The add-in does not collect, transmit, or process any other data. It has no
analytics, no telemetry, no crash reporting, no advertising, and makes no
network connections of any kind.

---

## 2. Third parties

Wall Slot Generator does not share any data with any third party. There are no
analytics tools, advertising networks, third-party SDKs, or affiliate entities
involved in the operation of this add-in. No user data leaves your local machine.

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

Because no data is transmitted to or stored by M2 Design or any third party,
there is no account to delete and no remote data to request removal of.

To remove all data stored by Wall Slot Generator on your local machine:

1. Open the Fusion 360 document in which you used the add-in
2. Go to **Tools → Scripts and Add-Ins → Add-Ins**, select Wall Slot Generator,
   and click **Stop**
3. Open the **Data Panel**, right-click the document, and choose
   **View Details on Web**, then use Autodesk's account data tools if desired
4. Alternatively, delete or close the Fusion 360 document — this removes all
   stored preferences associated with it

To uninstall the add-in entirely, remove the `wall_slots` folder from your
Fusion 360 AddIns directory. This removes the add-in and prevents any future
data from being stored.

For any privacy questions or requests, contact: [your contact email]

---

*This policy applies solely to the Wall Slot Generator add-in. It does not
apply to Autodesk Fusion 360 itself, which has its own privacy policy at
https://www.autodesk.com/company/legal-notices-trademarks/privacy-statement.*
