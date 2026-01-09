# from salesforce_auth_manager import StorageManager

# def test_storage_manager():
#     # Connect
#     user_id = "test_user"
#     # Create report
#     report_id = StorageManager.add_report(
#         user_id=user_id,
#         report_data={
#             'id': "000-000-000-000",
#             'column': "235345",
#             'type': "info",
#             'message': "235345",
#             'status': "100"
#         },
#         report_name='Monthly Test Report',
#         metadata={
#         'column_scores': [{'name': "col1", 'value': 10}, {'name': "col2", 'value': 45}, {'name': "col3", 'value': 32}, {'name': "col4", 'value': 93}],
#         'null_score': [7, 10],
#         'report_score': 85,
#         }
#     )

#     # List all reports (metadata only)
#     reports = StorageManager.get_report_list(user_id)

#     # Get full data when needed
#     data = StorageManager.get_report_data(user_id, report_id)

#     if data and reports:
#         print("DATA", data)
#         print("REPORTS", reports)
#         assert True
#     else: 
#         assert False

# test_storage_manager()

# # Example usage
# if __name__ == '__main__':
    

#     user_id = 'user123'
    
#     # Add reports
#     print("Adding reports...")
#     report1_id = StorageManager.add_report(
#         user_id=user_id,
#         report_data={
#             'sales': 50000,
#             'items': ['A', 'B', 'C']
#         },
#         report_name='January Sales',
#         report_type='Monthly',
#         status='completed'
#     )
#     print(f"✓ Created report: {report1_id}")
    
#     report2_id = storage.add_report(
#         user_id=user_id,
#         report_data={
#             'sales': 65000,
#             'items': ['D', 'E', 'F']
#         },
#         report_name='February Sales',
#         report_type='Monthly',
#         status='draft'
#     )
#     print(f"✓ Created report: {report2_id}")
    
#     # Get just the metadata list (lightweight)
#     print("\nReport metadata list:")
#     metadata = storage.get_report_list(user_id)
#     for meta in metadata:
#         print(f"  - {meta['name']} ({meta['type']}) - {meta['status']}")
    
#     # Get specific report data
#     print(f"\nReport 1 data:")
#     data = storage.get_report_data(user_id, report1_id) or {}
#     print(f"  Sales: ${data['sales']:,}")
#     print(f"  Items: {data['items']}")
    
#     # Get everything at once
#     print("\nAll reports:")
#     all_reports = storage.get_all_reports(user_id)
#     print(f"  Metadata entries: {len(all_reports['metadata'])}")
#     print(f"  Data entries: {len(all_reports['data'])}")
    
#     # Update report
#     print("\nUpdating report...")
#     storage.update_report(
#         user_id=user_id,
#         report_id=report1_id,
#         report_data={'sales': 55000, 'items': ['A', 'B', 'C', 'D']},
#         status='published'
#     )
#     print("✓ Report updated")
    
#     # Delete report
#     print("\nDeleting report...")
#     storage.delete_report(user_id, report2_id)
#     print("✓ Report deleted")
    
#     # Check final state
#     print("\nFinal report list:")
#     metadata = storage.get_report_list(user_id)
#     for meta in metadata:
#         print(f"  - {meta['name']} ({meta['status']})")