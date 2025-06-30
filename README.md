# Moving Intelligence Integration for Home Assistant
<p align="left">
  <a href="https://github.com/hacs/default" target="_blank"><img src="https://img.shields.io/badge/HACS-Default-53b3ff.svg?style=for-the-badge" alt="HACS Default"></a>
  <a href="https://github.com/Raznor09" target="_blank"><img src="https://img.shields.io/badge/GitHub-Raznor09-7e1ab2?style=for-the-badge&logo=github" alt="Raznor09 on GitHub"></a>
    
  <a href="https://github.com/Raznor09/moving_intelligence/releases/latest" target="_blank"><img src="https://img.shields.io/github/v/release/Raznor09/moving_intelligence?style=for-the-badge&label=Release&color=1ab21a" alt="GitHub Release"></a>
  
  <a href="https://github.com/Raznor09/moving_intelligence/releases" target="_blank"><img src="https://img.shields.io/github/downloads/Raznor09/moving_intelligence/total?style=for-the-badge&color=ff1a1a" alt="Total Downloads"></a>
  <a href="https://coff.ee/raznor09" target="_blank"><img src="https://img.shields.io/badge/COFFEE-ffb21a?style=for-the-badge&label=BUY%20ME%20A" alt="Buy me a coffee"></a>
</p>
</p>
<img src="https://cdn.shopify.com/s/files/1/0121/0220/5499/files/MicrosoftTeams-image_18.png" alt="Moving Intelligence" width="400px">

---

This is a repaired and improved custom integration to connect your Moving Intelligence equipped vehicle(s) with Home Assistant.

This integration provides:
- A `device_tracker` entity that shows the last known parked location of your vehicle.
- Attributes for , odometer, last trip address, brand, model, license plate, color, year, and chassis number, which can be used to create template sensors.
  
**Note**
 To use this integration, you need a valid user account and an API key provided by the Moving Intelligence support team. 
 You can request one by sending an email to aftersales@movingintelligence.nl.

---

## Installation

### HACS (Recommended)

1. Ensure you have [HACS](https://hacs.xyz/docs/use/).
2. In Home Assistant, go to **HACS** > **Integrations**.
3. Click the three-dots menu in the top right corner and select **Custom repositories**.
4. In the `Repository` field, add the following URL: 

        https://github.com/Raznor09/moving_intelligence

5. In the `Category` dropdown, select **Integration**.
6. Click **Add**.
7. The `Moving Intelligence` will now appear in your HACS store. Click on it, and then click on **Download**
8. In the window that pops up, click the **Download** button again to install.
9. Restart Home Assistant when prompted.

---

<details>
<summary><b>Manual Installation</b></summary>

1. Go to the [latest release](https://github.com/Raznor09/moving_intelligence/releases/latest) on GitHub.
2. Download the `moving_intelligence.zip` file attached to the release.
3. Unpack the downloaded zip file.
4. Copy the `moving_intelligence` directory into your `<config_dir>/custom_components/` directory in Home Assistant.
5. Restart Home Assistant.

</details>

---

## Configuration

1. After installing via HACS or manually and restarting Home Assistant, go to **Settings** > **Devices & Services**.
2. Click the **+ Add Integration** button in the bottom right corner.
3. Search for `Moving Intelligence` and select it from the list.
4. Follow the on-screen instructions and enter your Moving Intelligence **Username** and **API key** when prompted.
5. If your credentials are correct, you will see a success confirmation (**reauth_successful**).
6. The integration will be set up and your vehicle(s) will be added as devices to Home Assistant.

---

## Example: Create Template Sensors

This section shows how to create individual sensors for all your vehicle's data attributes.

**1. Go to your `templates.yaml` file** (or `configuration.yaml` under a `template:` key).

**2. Copy and paste the code below.** You must replace `device_tracker.your_vehicle_entity_id` in the code with the actual entity ID of your car.

   >*__How to find your entity ID:__ Go to **Settings** > **Devices & Services** > find **Moving Intelligence** > **Select Entities** > **Search for your vehicle** > **Click on it** > **Select Settings (gear icon top right)** > **Copy Entity ID.**

```yaml
- sensor:
    # --- General Vehicle Information ---
    - name: "Vehicle Brand"
      unique_id: moving_intelligence_vehicle_brand
      state: "{{ state_attr('device_tracker.your_vehicle_entity_id', 'brand') }}"
      icon: mdi:car-info

    - name: "Vehicle Model"
      unique_id: moving_intelligence_vehicle_model
      state: "{{ state_attr('device_tracker.your_vehicle_entity_id', 'model') }}"
      icon: mdi:car-side

    - name: "Vehicle License Plate"
      unique_id: moving_intelligence_vehicle_license_plate
      state: "{{ state_attr('device_tracker.your_vehicle_entity_id', 'licence') }}"
      icon: mdi:alphabetical-variant

    - name: "Vehicle Color"
      unique_id: moving_intelligence_vehicle_color
      state: "{{ state_attr('device_tracker.your_vehicle_entity_id', 'color') }}"
      icon: mdi:palette

    - name: "Vehicle Year"
      unique_id: moving_intelligence_vehicle_year
      state: "{{ state_attr('device_tracker.your_vehicle_entity_id', 'yearOfManufacture') }}"
      icon: mdi:calendar

    - name: "Vehicle Chassis Number"
      unique_id: moving_intelligence_vehicle_chassis_number
      state: "{{ state_attr('device_tracker.your_vehicle_entity_id', 'chassisNumber') }}"
      icon: mdi:barcode

    # --- Dynamic Data ---
    - name: "Vehicle Odometer"
      unique_id: moving_intelligence_vehicle_odometer
      state: "{{ state_attr('device_tracker.your_vehicle_entity_id', 'odometer') | int(0) }}"
      unit_of_measurement: "km"
      icon: mdi:road-variant

    - name: "Vehicle Address"
      unique_id: moving_intelligence_vehicle_address
      state: "{{ state_attr('device_tracker.your_vehicle_entity_id', 'end_trip_address') or 'Unknown' }}"
      icon: mdi:map-marker
```
---

## Example: Lovelace Card

Once you have created the template sensors and reloaded them, you can display them on your dashboard with an Entities card.

```yaml
        
        type: entities
        title: Vehicle Details
        entities:
          - entity: sensor.vehicle_brand
          - entity: sensor.vehicle_model
          - entity: sensor.vehicle_license_plate
          - type: divider
          - entity: sensor.vehicle_color
          - entity: sensor.vehicle_year
          - entity: sensor.vehicle_chassis_number
          - type: divider
          - entity: sensor.vehicle_odometer
          - entity: device_tracker.your_vehicle_entity_id
            name: Location Status
          - entity: sensor.vehicle_address
```
---

<img src="https://github.com/Raznor09/moving_intelligence/blob/main/images/Vehicle_details.png" alt="Lovelace Card Example" width="400"/>

---
## Support the Project

This integration is maintained with great pleasure. If you appreciate this integration and would like to support my work, please consider a small donation. Every contribution is highly valued!

<a href="https://coff.ee/raznor09" target="_blank" rel="noreferrer noopener"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-blue.png" alt="Buy Me A Coffee" width="150px"></a>

---

## Disclaimer & Dependencies

- This is an unofficial, community-maintained integration. It is not affiliated with or supported by Moving Intelligence
- This repaired version is maintained by [@Raznor09](https://github.com/Raznor09).
- All credits for the original integration go to [@cyberjunky](https://github.com/cyberjunky/home-assistant-moving_intelligence).
- The API documentation used for this integration can be found at the official [Api Website](https://api-app.movingintelligence.com/) of Moving Intelligence.
- The functionality of this integration is completely dependent on the availability of the Moving Intelligence platform and their public API.
- **If the Moving Intelligence services are down for maintenance or due to an outage, this integration will not work.**
