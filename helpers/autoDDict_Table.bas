Attribute VB_Name = "Module1"
Sub UpdateOrCreateDictFieldsSheet()
    Dim wb As Workbook
    Dim ws As Worksheet
    Dim dictWs As Worksheet
    Dim wsName As String
    Dim table As ListObject
    Dim column As ListColumn
    Dim nextRow As Long
    Dim ExcludeSheets As Variant
    Dim sheetName As Variant
    Dim exclude As Boolean
    
    ' Set the name for the dictionary fields sheet
    wsName = "tables_infos"
    
    ' Reference the active workbook
    Set wb = ActiveWorkbook
    
    CreateDictFieldsSheet
    
    ' Retrieve the created sheet
    On Error Resume Next
    Set dictWs = wb.Sheets(wsName)
    On Error GoTo 0
    
    ' Exit if still not found
    If dictWs Is Nothing Then
        MsgBox "Error creating or retrieving dict_fields sheet.", vbExclamation
        Exit Sub
    End If
    
    ' Define sheets to exclude
    ExcludeSheets = Array("DDict_tables", "DDict_attributes", "meta_references")
    
    ' Find the next available row in dict_fields sheet
    nextRow = dictWs.Cells(dictWs.Rows.Count, 1).End(xlUp).Row + 1
  
    ' Loop through each worksheet in the workbook
    For Each ws In wb.Worksheets
        exclude = False
        
        ' Check if the sheet name is in the exclusion list
        For Each sheetName In ExcludeSheets
            If ws.Name = sheetName Then
                exclude = True
                Exit For
            End If
        Next sheetName
        
        ' Skip the sheet if it's in the exclusion list or if it's the dict_fields sheet
        If Not exclude And ws.Name <> wsName Then
            ' Check if the worksheet has tables (ListObjects)
            If ws.ListObjects.Count > 0 Then
                ' Loop through each table in the worksheet
                For Each table In ws.ListObjects
                    ' Loop through each column in the table
                    For Each column In table.ListColumns
                        ' Add the worksheet name and column name to the dict_fields sheet
                        dictWs.Cells(nextRow, 1).Value = ws.Name
                        dictWs.Cells(nextRow, 2).Value = column.Name
                        nextRow = nextRow + 1
                    Next column
                Next table
            End If
        End If
    Next ws
    
    ' Autofit columns A to E for better visibility
    dictWs.columns("A:E").AutoFit
    
    ' Confirm completion
    MsgBox "Sheet '" & wsName & "' updated with table names and attributes.", vbInformation
End Sub

Sub CreateDictFieldsSheet()
    Dim ws As Worksheet
    Dim wsName As String
    Dim dictWs As Worksheet
    
    ' Set the name for the dictionary fields sheet
    wsName = "tables_infos"
    
    ' Reference the active workbook
    Dim wb As Workbook
    Set wb = ActiveWorkbook
    
    ' Check if the dict_fields sheet already exists
    On Error Resume Next
    Set dictWs = wb.Sheets(wsName)
    On Error GoTo 0
    
    ' If the dict_fields sheet already exists, ask for confirmation to delete it
    If Not dictWs Is Nothing Then
        Dim response As VbMsgBoxResult
        response = MsgBox("The sheet '" & wsName & "' already exists. Do you want to delete it and create a new one?", vbYesNo + vbQuestion, "Sheet Exists")
        
        If response = vbYes Then
            Application.DisplayAlerts = False
            dictWs.Delete
            Application.DisplayAlerts = True
        Else
            MsgBox "Operation cancelled. The sheet '" & wsName & "' was not deleted.", vbInformation
            Exit Sub
        End If
    End If
    
    ' Add a new sheet
    On Error Resume Next
    Set dictWs = wb.Sheets.Add(After:=wb.Sheets(wb.Sheets.Count))
    If Err.Number <> 0 Then
        MsgBox "Unable to add a new sheet. Please try again.", vbCritical
        Exit Sub
    End If
    On Error GoTo 0
    
    ' Rename the new sheet
    dictWs.Name = wsName
    
    ' Initialize the header row
    dictWs.Cells(1, 1).Value = "Table"
    dictWs.Cells(1, 2).Value = "Attribute"
    dictWs.Cells(1, 3).Value = "isPK"
    dictWs.Cells(1, 4).Value = "isFK"
    dictWs.Cells(1, 5).Value = "ReferenceTable"
    
    ' Confirm sheet creation
    MsgBox "Sheet '" & wsName & "' created with columns Table and Attribute.", vbInformation
End Sub


Sub ConvertToTables()
    Dim ws As Worksheet
    Dim tbl As ListObject
    Dim rng As Range
    
    ' Loop through each worksheet in the active workbook
    For Each ws In ActiveWorkbook.Worksheets
        ' Determine the range of data (assumes data starts from A1 and there are no empty columns or rows in between)
        Set rng = ws.Range("A1").CurrentRegion
        
        ' Add a new table (ListObject) starting from cell A1
        Set tbl = ws.ListObjects.Add(xlSrcRange, rng, , xlYes)
        
        ' Assign headers based on the first row of the range
        tbl.HeaderRowRange.Value = ws.Range("A1").Resize(1, rng.columns.Count).Value
        
        ' Optional: Format the table as a proper Excel table
        tbl.TableStyle = "TableStyleMedium2" ' You can change this to any built-in table style
        
        ' Resize the range to exclude the header row (if needed)
        Set rng = rng.Offset(1).Resize(rng.Rows.Count - 1, rng.columns.Count)
    Next ws
End Sub

