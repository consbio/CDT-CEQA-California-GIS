SELECT parcel_id
FROM   mike_gough.parcel_exemptions l 
WHERE  NOT EXISTS (
   SELECT
   FROM   mike_gough.sacramento_parcels
   WHERE  parcel_id = l.parcel_id
   );