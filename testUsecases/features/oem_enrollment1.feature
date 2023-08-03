@DT_NETWORK
Feature: OEM Enrollment - Phase 1

  @OEM_ENROLLMENT1
  Scenario: Dave enrolls OEM
    Given Dave is on the consortium's marketing website
    When Dave taps the "Enroll OEM" button
    Then the marketing website makes a request to the C:1 Admin API to obtain an Out-of-Band (OOB) URI
    And C:1 generates a UUID for the transaction and stores it in the "Transaction Table"
    And C:1 creates the OOB and the goal code c2dt.consortium.enroll.OEM?UUID
    And the marketing website redirects Dave to a new page containing the OOB URI and enrollment instructions
    And Dave reads and understands the instructions for deploying the OEM's DIDComm Agent (O:1)

  @OEM_ENROLLMENT1
  Scenario: OEM staff deploys DIDComm Agent
    Given the OEM staff is prepared to deploy the DIDComm Agent
    When the OEM staff deploys the DIDComm Agent
    Then the OEM staff initiates the agent's startup process
    And O:1 generates its public DID during the initial boot

  @OEM_ENROLLMENT1
  Scenario: D:1 establishes connection with C:1
    Given D:1 has received the OOB URI
    When D:1 clicks the OOB URI
    Then D:1's smart wallet opens through a deep link
    And D:1 establishes a connection with C:1 using the OOB URI

  @OEM_ENROLLMENT1
  Scenario: C:1 recognizes goal code UUID and creates entry in Agent Table
    Given D:1 has established a connection with C:1 using the OOB URI
    When C:1 identifies the goal code UUID
    Then C:1 adds a new entry to the Agent Table

  @OEM_ENROLLMENT1
  Scenario: D:1 establishes connection with O:1
    Given D:1 has established a connection with C:1
    When D:1 establishes a connection with O:1 using an implicit invitation
    Then the connection between D:1 and O:1 is established