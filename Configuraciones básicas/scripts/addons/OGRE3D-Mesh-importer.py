#!BPY

"""
Name: 'OGRE3D Mesh Importer'
Blender: 2.41
Group: 'Import'
Tip: 'import a OGRE3D (.mesh,.mesh.xml) File'
"""

__author__="Daniel (D-Man) Handke"

__version__="1.00"

__bpydoc__="""OGRE3D_Mesh_importer.py

OGRE Mesh and Character Importer by D-Man

imports OGRE Mesh 'mesh.xml' and assigned skeleton files

you will need the OgreXMLConverter from the OGRE XML Command Line Tools

To get them go for http://www.ogre3d.org


""" 

# ***** BEGIN GPL LICENSE BLOCK *****
#
# Script copyright (C) Daniel Handke
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# ***** END GPL LICENCE BLOCK *****
# --------------------------------------------------------------------------
 



from Blender import *
from Blender.Mathutils import *
from Blender import Armature as A
from Blender.BGL import *
from math import *
import os

# Test if File is a valid mesh.xml file	
		
def isValidFile(lines):
	if '<mesh>' in lines[0]:
		isValid = 'true'
	else:
		isValid = 'false'
		
	return isValid


#########################################
#										#
#	Get Objects Data LineIndexes		#
#										#
#########################################						
		
def getObjectsData(lines):
	objectsdata = []
	meshdata = []
	if isValidFile(lines) == 'true':
		counter = 0
		counter2 = 0
		for line in lines:
			objectsdict = {}
			if '<submesh ' in line:
				if '/' not in line:
					a = line.find('material="')
					b = line.find('useshared')
					name = line[a+10:b-2]+str(counter2)
					counter2 += 1
				else:
					a = line.find('/')
					b = line.find('useshared')
					name = line[a+1:b-2]+str(counter2)
					counter2 += 1
				objectsdict['name'] = name
				objectsdict['startline'] = counter
			if len(objectsdict) > 0:	
				objectsdata.append(objectsdict)
			counter += 1
	
	for ob in objectsdata:
		obdata = {}
		obdata['name'] = ob['name']
		hastexcoords = 0
		for i in range(ob['startline'],len(lines)):
			if '<faces ' in lines[i]:
				obdata['facesstart'] = i
			if '</faces>' in lines[i]:
				obdata['facesend'] = i
			if 'vertexbuffer pos' in lines[i] and not 'texture_coords' in lines[i]:
				obdata['vertstart'] = i
			if 'vertexbuffer pos' in lines[i] and 'texture_coords' in lines[i]:
				obdata['vertstart'] = i
				obdata['texstart'] = i
				hastexcoords = 1
			if 'vertexbuffer tex' in lines[i]:
				obdata['vertend'] = i-1
				obdata['texstart'] = i
			if '/geometry>' in lines[i] and hastexcoords == 0:
				obdata['texend'] = i-1
			if '/geometry>' in lines[i] and hastexcoords == 1:
				obdata['vertend'] = i-1
				obdata['texend'] = i-1			
			if '<boneassignments>' in lines[i]:
				obdata['boneassignstart'] = i
			if '</boneassignments>' in lines[i]:
				obdata['boneassignend'] = i
				
			if '</submesh>' in lines[i]:
				break
			
		meshdata.append(obdata)	
	
	return meshdata


#########################################
#										#
# 	Get Lists of VertexValues			#
#										#
#########################################

def getVertexList(lines):
	objs = getObjectsData(lines)
	vertexlists = []
	for ob in objs:
		vertexlist = []
		for i in range(ob['vertstart'],ob['vertend']):
			
			if '<position ' in lines[i]:
				vpos1 = lines[i].find('x="')
				vpos2 = lines[i].find('y="')
				vpos3 = lines[i].find('z="')
				vpos4 = lines[i].find('/>')
				xpos = float(lines[i][vpos1+3:vpos2-2])
				ypos = float(lines[i][vpos2+3:vpos3-2])
				zpos = float(lines[i][vpos3+3:vpos4-2])
				vertex = [xpos,-zpos,ypos]
				vertexlist.append(vertex)
		vertexlists.append(vertexlist)
	return vertexlists


#########################################
#										#
# 	Get Lists of NormalValues			#
#										#
#########################################
	
def getNormalsList(lines):
	objs = getObjectsData(lines)
	normallists = []
	for ob in objs:
		normallist = []
		for i in range(ob['vertstart'],ob['vertend']):
			if '<normal ' in lines[i]:
				npos1 = lines[i].find('x="')
				npos2 = lines[i].find('y="')
				npos3 = lines[i].find('z="')
				npos4 = lines[i].find('/>')
				xpos = float(lines[i][npos1+3:npos2-2])
				ypos = float(lines[i][npos2+3:npos3-2])
				zpos = float(lines[i][npos3+3:npos4-2])
				
				normal = [xpos,-zpos,ypos]
				normallist.append(normal)
		normallists.append(normallist)
	return normallists

#########################################
#										#
# 	Get Lists of TexCoordValues			#
#										#
#########################################

def getTexCoordList(lines):
	objs = getObjectsData(lines)
	texcoordlists = []
	a = 0
	for ob in objs:
		texcoordlist = []
		for i in range(ob['texstart'],ob['texend']):
			if '<texcoord ' in lines[i]:
				tpos1 = lines[i].find('u="')
				tpos2 = lines[i].find('v="')
				tposW = lines[i].find('w="')
				tpos3 = lines[i].find('/>')
				upos = float(lines[i][tpos1+3:tpos2-2])
				#print "another string: " + lines[i]
				if tposW != -1:
					vpos = float(lines[i][tpos2+3:tposW-2])
				else:
					vpos = float(lines[i][tpos2+3:tpos3-2])
				uvco = [upos,1-vpos]
				if i - a > 2:
					texcoordlist.append(uvco)
				a = i
		texcoordlists.append(texcoordlist)
	return texcoordlists


#########################################
#										#
# 	Get Lists of FaceIndexes			#
#										#
#########################################

def getFaceIndexList(zeilen):
	objs = getObjectsData(zeilen)
	faceindlists = []
	for ob in objs:
		faceindlist = []
		for i in range(ob['facesstart'],ob['facesend']):
			if '<face ' in zeilen[i]:
				ipos1 = zeilen[i].find('v1="')
				ipos2 = zeilen[i].find('v2="')
				ipos3 = zeilen[i].find('v3="')
				ipos4 = zeilen[i].find('/>')
				f1 = long(zeilen[i][ipos1+4:ipos2-2])
				f2 = long(zeilen[i][ipos2+4:ipos3-2])
				f3 = long(zeilen[i][ipos3+4:ipos4-2])
				face = [f1,f2,f3]
				faceindlist.append(face)
		faceindlists.append(faceindlist)
	return faceindlists

#########################################
#										#
#	Get the Vertex Skeleton Bindings	#
#										#
#########################################

def getBoneAssignments(lines):
	objs = getObjectsData(lines)
	boneasslists = []
	for ob in objs:
		boneasslist = []
		for i in range(ob['boneassignstart'],ob['boneassignend']):
			if '<vertexboneassignment ' in lines[i]:
				bpos1 = lines[i].find('vertexindex="')
				bpos2 = lines[i].find('boneindex="')
				bpos3 = lines[i].find('weight="')
				bpos4 = lines[i].find('/>')
				vi = lines[i][bpos1+13:bpos2-2]
				bi = lines[i][bpos2+11:bpos3-2]
				wgt = lines[i][bpos3+8:bpos4-2]
				vil = [int(vi)]
				boneass = [int(bi),vil,float(wgt)]
				boneasslist.append(boneass)
		boneasslists.append(boneasslist)
	return boneasslists


#########################################
#										#
#	get Material Names					#
#########################################

def getMaterials(lines):
	Materials=[]
	for i in range(0,len(lines)):
		if 'material="' in lines[i]:
			mat1 = lines[i].find('material="')
			mat2 = lines[i].find('useshared')
			matname = lines[i][mat1+10:mat2-2]
			Materials.append(matname)
			print matname
	return Materials

#########################################
#										#
#		Get Texture FileNames			#
#										#
#########################################

def getTextures(lines,dirname):
	
	textures = []
	materials = getMaterials(lines)
	print materials
	filename = materials[0]
	print "FileName:" ,dirname+"/"+materials[0]+".material"
	print filename
	try:
		matfile = open(dirname+"/"+filename+".material")
		print "MaterialFile found"
	except:
		return textures
	matlines = matfile.readlines()
	matstart = []
	
	
	#print "Materials"
	for mat in materials:
		print mat
		
		for i in range(0,len(matlines)):
			if mat+"\n" in matlines[i] and 'material' in matlines[i]:
				matstart.append(i)
				print i
				
	for start in matstart:
		for i in range(start,len(matlines)):
			if 'texture ' in matlines[i]:
				tn1 = matlines[i].find('texture ')
				tn2 = matlines[i].find('.')
				name = matlines[i][tn1+8:tn2]
				print name
				ext = matlines[i][tn2:tn2+4]
				print ext
				filename = name+ext
				textures.append(filename)
				break
				
	return textures

#########################################
#										#
# 			Draw the Meshes				#
#										#
#########################################

def createMesh(lines,dirname):
	
	vertposlist = getVertexList(lines)
	normalslist = getNormalsList(lines)
	texcoords = getTexCoordList(lines)
	textures = getTextures(lines,dirname)
	faceindexes = getFaceIndexList(lines)
	objs = getObjectsData(lines)
	global sf
	
	scn = Scene.getCurrent()
	
	for i in range(0,len(objs)):
		objsname = objs[i]['name']
		newMesh = Object.New('Mesh',objsname)
		Figure = NMesh.GetRaw()
		FigureMat = Material.New(objsname+'mat')
		FigureTex = Texture.New(objsname+'tex')
		FigureTex.setType('Image')
		try:
			img = Image.Load(dirname+"/"+textures[i])
			FigureTex.image = img
		except:
			print "Skipped Image File"		
		FigureMat.setRef(1.0)
		FigureMat.setTexture(0,FigureTex,Texture.TexCo.UV,Texture.MapTo.COL)
		FigureMat.setSpec(0.0)
		FigureMat.setHardness(1)
		FigureMat.setRGBCol(122,122,122)
		Figure.materials.append(FigureMat)
		
		# create Vertieces
		
		vertices = vertposlist[i]
		normals = vertposlist[i]
		uvcoords = texcoords[i]
		faceindex = faceindexes[i]
		
		for j in range(0,len(vertices)):
			vertex = vertices[j]
			normal = normals[j]
			uvcoord = uvcoords[j]
			v = NMesh.Vert(vertex[0]*sf,vertex[1]*sf,vertex[2]*sf)
			v.no[0] = normal[0]*sf
			v.no[1] = normal[1]*sf
			v.no[2] = normal[2]*sf
			v.uvco[0] = uvcoord[0]*sf
			v.uvco[1] = uvcoord[1]*sf
			Figure.verts.append(v)
		
		# Create Faces
		
		for j in range(0,len(faceindex)):
			f = NMesh.Face()
			f.v.append(Figure.verts[faceindex[j][0]])
			f.v.append(Figure.verts[faceindex[j][1]])
			f.v.append(Figure.verts[faceindex[j][2]])	
			f.uv.append((uvcoords[faceindex[j][0]][0],uvcoords[faceindex[j][0]][1]))
			f.uv.append((uvcoords[faceindex[j][1]][0],uvcoords[faceindex[j][1]][1]))
			f.uv.append((uvcoords[faceindex[j][2]][0],uvcoords[faceindex[j][2]][1]))
			f.smooth = 1
			try:
				f.image = img
				Figure.faces.append(f)
			except:
				Figure.faces.append(f)
		
		Figure.hasFaceUV(1)
		
		
		newMesh.link(Figure)
		scn.link(newMesh)
	Redraw()
	
#########################################
#										#
#	Get the Skeletons File Name			#
#										#
#########################################

def getSkeletonFile(lines):
	line = lines[len(lines)-2]
	if '<skeletonlink ' in line:
		n1 = line.find('name="')
		n2 = line.find('/>')
		name = line[n1+6:n2-2]
	elif '<skeletonlink' not in line:
		name = None
			
	return name

###############################################
###############################################
#											  #
#		Skeleton Creation					  #
#											  #
###############################################

###############################################
#                                             #
#		Getting the Bone Values	              #
#                                             #
###############################################


	
def getElements(lines):

	
	boneid = []
	bonename = []
	boneposition = []
	boneangle = []
	
	boneaxis = []
	bonelocation = []
	parentid = []
	bonesdictlist = []	
	for i in range(0,len(lines)):
		bonesdict = {}
		
		# find bone data name id rot pos axis
		if '<bone id' in lines[i]:
			
			n1 = lines[i].find('id="')
			n2 = lines[i].find('name="')
			n3 = lines[i].find('">')
			bid = lines[i][n1+4:n2-2]
			# find bonename, boneid
			boneid.append(int(bid))
			bonesdict['id'] = bid
			name = lines[i][n2+6:n3]
			if len(name) > 18:
				cutter = len(name)-18
			else:
				cutter = 0
			
			bonesdict['name'] = name[+cutter:]
			# find x,y,z position of bone
			xp1 = lines[i+1].find('x="')
			yp1 = lines[i+1].find('y="')
			zp1 = lines[i+1].find('z="')
			ep1 = lines[i+1].find('/>')
			xp = float(lines[i+1][xp1+3:yp1-2])
			yp = float(lines[i+1][yp1+3:zp1-2])
			zp = float(lines[i+1][zp1+3:ep1-2])
			pos = [xp,-zp,yp]
			bonesdict['position'] = pos
			# find rotation angle of bone
			rp1 = lines[i+2].find('angle="')
			rp2 = lines[i+2].find('">')
			angle = float(lines[i+2][rp1+7:rp2])
			bonesdict['angle'] = angle
			# find x,y,z axis of bone
			xa1 = lines[i+3].find('x="')
			ya1 = lines[i+3].find('y="')
			za1 = lines[i+3].find('z="')
			ea1 = lines[i+3].find('/>')
			xa = float(lines[i+3][xa1+3:ya1-2])
			ya = float(lines[i+3][ya1+3:za1-2])
			za = float(lines[i+3][za1+3:ea1-2])
			axis = [xa,-za,ya]
			bonesdict['axis'] = axis
			bonesdictlist.append(bonesdict)
		

	return bonesdictlist

###############################################
#                                             #
#		Getting the Bone Hirarchy             #
#                                             #
###############################################
	
		
def getHirarchy(lines):
	boneparent = []
	bonehirarchy = []
	for line in lines:
		
		if '<boneparent' in line:
			cutter = 0
			bp1 = line.find('bone="')
			bp2 = line.find('parent="')
			bpe = line.find('/>')
			bone = line[bp1+6:bp2-2]
			if len(bone) > 18:
				cutter = len(bone)-18
			else:
				cutter = 0
			
		
			parent = line[bp2+8:bpe-2]
			if len(parent) > 18:
				cutter2 = len(parent)-18
			else:
				cutter2 = 0
			
			boneparent = [bone[+cutter:],parent[+cutter2:]]
			bonehirarchy.append(boneparent)
	
	return bonehirarchy




	

###############################################
#                                             #
#		Getting the Endbones	              #
#                                             #
###############################################

def getEndbones(lines):

	boneshirarchy = getHirarchy(lines)
	bonechild = []
	boneparent = []
	endbonebp = []
	
	for bonepair in boneshirarchy:
		
		bonechild.append(bonepair[0])
		boneparent.append(bonepair[1])
		
	for i in range(0,len(bonechild)):
		counter = 0
		for j in range(0,len(boneparent)):
			if bonechild[i] == boneparent[j]:
				counter += 1
		if counter == 0:
			parent = bonechild[i]
			child = bonechild[i]+"E"
			bpnoc = [child,parent]
			endbonebp.append(bpnoc)
			
	return endbonebp

###############################################
#                                             #
#		Getting the EndBone Parent ID's       #
#                                             #
###############################################


	

def getEndParentid(lines):

	endboneparentid = []

	counter = 0
	for a in getElements(lines):
		for j in getEndbones(lines):
			if a['name'] == j[1]:	
				endboneparentid.append(counter)
				#print a['name'],counter
		counter += 1	
	
	return endboneparentid
	


###############################################
#                                             #
#	Making the Bone Quatrotation an Euler     #
#                                             #
###############################################
	
def rotQuattoEuler(a):
		

	angle = degrees(a['angle'])
	axis = (a['axis'][0],a['axis'][1],a['axis'][2])
	quat = Quaternion(axis,angle)
	euler = quat.toEuler()
	torad = Euler(euler)
	
	return torad
	

###############################################
#                                             #
# Creating Temp Empties and set them to Scene #
#                                             #
###############################################
	
def createEmpties(lines):
	global sf
	scn = Scene.getCurrent()

	# add empties

	for a in getElements(lines):
		ob = Object.New('Empty',a['name'])
		
		
	
	# add end empties


	for a in getEndbones(lines):
		ob = Object.New('Empty',a[0])
		
		
	
	# create empties hirarchy
	for a in getHirarchy(lines):
		ob = Object.Get(a[1])
		ob2 = Object.Get(a[0])
		oblist = [ob2]
		ob.makeParent(oblist,1,0)

	# parenting end empties


	for a in getEndbones(lines):
		ob = Object.Get(a[1])
		ob2 = Object.Get(a[0])
		oblist = [ob2]
		ob.makeParent(oblist,1,0)


	# set empties positions and rotations


	for a in getElements(lines):
		ob = Object.Get(a['name'])
		#scn.link(ob)
		bl = a['position']
		ob.setLocation(bl[0]*sf,bl[1]*sf,bl[2]*sf)
		
		rot = Euler(rotQuattoEuler(a))
		rotx = rot.x
		roty = rot.y
		rotz = rot.z
		ob.setEuler(radians(rotx),radians(roty),radians(rotz))
			
	# set end empties positions and rotations

	for a in getEndbones(lines):
		ob = Object.Get(a[0])
		#scn.link(ob)
		ob.LocY = -10*sf
	
#########################################
#										#
#		Getting the skeletons root		#
#										#
#########################################


def getRoots():
	emplist = []
	rootlist = []
	objs = Object.Get()
	for obj in objs:
		if obj.getType() == 'Empty':
			emplist.append(obj)
	
	for em in emplist:
		if em.getParent() == None:
			rootlist.append(em.name)
			
	
	return rootlist

#########################################
#										#
# Create List of Temp Emptys			#
#										#
#########################################

def createEmptylist(lines):
	
	elnames = []
	endbones = getEndbones(lines)
	elements = getElements(lines)
	for el in elements:
		elnames.append(el['name'])
	for eb in endbones:
		elnames.append(eb[0])
		
	return elnames
	

#########################################
#										#
# Getting Armature and its Bone Names	#
#										#
#########################################

def getArmatureBones(lines):
	rootbones = getRoots()
	elnames= createEmptylist(lines)
	elcomp = []
	armature = []
	for root in rootbones:
		bonenames = []
		if root in elnames:
			bonenames.append(root) 
			
			for el in elnames:
				objs = Object.Get(el)	
				
				if objs.getParent() != None and el not in elcomp:
					bonenames.append(el)
				elcomp.append(el)
				
		armature.append(bonenames)		
	return armature

#########################################
#										#
#			Create Amatures				#
#										#
#########################################

def createArmature(armatures,FileName):
	
	ArmatureList =[]
	counter = 0
	scn = Scene.getCurrent()
	for arms in armatures:
		bones = []
		aboneslist = []
		for bone in arms:
			bones.append(bone)
		newarmature = A.Armature('Ar'+FileName+str(counter))
		newarmobj = Object.New('Armature','Ar'+FileName+str(counter))
		newarm = A.Get('Ar'+FileName+str(counter))
		ArmatureList.append('Ar'+FileName+str(counter))
		
		
		for abone in bones:
				
			empty = Object.Get(abone)
			
			
			if empty.getParent() == None:
				newarm.makeEditable()
				newarm.drawType = A.OCTAHEDRON
				#newarm.drawNames = True
				vpos1 = empty.getMatrix('worldspace')[3]
				 
				eb = A.Editbone()
				eb.head = Vector(vpos1[0],vpos1[1]+15*sf,vpos1[2])
				eb.tail = Vector(vpos1[0],vpos1[1]+25*sf,vpos1[2])
				
			
				
				
				newarm.bones['Root'] = eb
				aboneslist.append(abone)
				
				eb = A.Editbone()
				eb.head = Vector(vpos1[0],vpos1[1],vpos1[2])
				eb.tail = Vector(vpos1[0],vpos1[1]+10*sf,vpos1[2])
				eb.parent = newarm.bones['Root']
				newarm.bones[abone] = eb
				
			else:
				newarm.makeEditable()
				newarm.drawType = A.OCTAHEDRON
				parent = empty.getParent()
								
				vpos1 = empty.getMatrix('worldspace')[3]
				vpos2 = parent.getMatrix('worldspace')[3]
				
				
				
				if parent.name not in aboneslist:
					eb = A.Editbone()
					eb.head = Vector(vpos2[0],vpos2[1],vpos2[2])
					eb.tail = Vector(vpos1[0],vpos1[1],vpos1[2])
														
					if parent.getParent() != None:
						pparent = parent.getParent() 
						print pparent.name
						eb.parent = newarm.bones[pparent.name]
					
					
					newarm.bones[parent.name] = eb
					aboneslist.append(parent.name)
					#print "  NewBone",abone
					
					
		newarmobj.link(newarm)
		scn.link(newarmobj)
		newarm.update()
		counter += 1
	return ArmatureList

#################################################
#												#
#		set the armature matrices to the empty  #
#			with inverted x rotation			#
#												#
#################################################
	
		
def setBoneMatrices(armatures):
	for armature in armatures:
		armobj = Object.Get(armature).getData()

		for bones in armobj.bones.keys():
			bone = armobj.bones[bones]
			if bones != 'Root':
			
				empty = Object.Get(bones)
				empmat = empty.getMatrix()
				emprot = empty.getMatrix().rotationPart().toEuler()
				emprot.x += 180
				quat = emprot.toQuat()
				newmat = RotationMatrix(quat.angle,4,"r",quat.axis)
				newmat[3][0] = empmat[3][0]
				newmat[3][1] = empmat[3][1]
				newmat[3][2] = empmat[3][2]
				armobj.makeEditable()
				armobj.bones[bones].matrix = newmat
				armobj.update()
				Redraw()	



	
#########################################
#										#
#	Get the Vertexgroups 				#
#										#
#########################################

def getVertexGroups(lines):
	vertgroups = []
	for bone in getElements(lines):
		vertgroups.append(bone['name'])
	return vertgroups

#################################################
#												#
# Create the Vertex Groups and Vertex Weights	#
#												#
#################################################

def createVertGroups(lines1,lines2,armatures):
	vertgroups = getVertexGroups(lines1)
	objectsdata = getObjectsData(lines2)
	boneass = getBoneAssignments(lines2)
	OBVertGroups = []
	for i in range(0,len(boneass)):
		
		assignment = boneass[i]
		VertexGroups = []
		#print objectsdata[i]['name']
		for j in range(0,len(assignment)):
			vertgroup = vertgroups[assignment[j][0]]
			if vertgroup not in VertexGroups:
				VertexGroups.append(vertgroup)
		OBVertGroups.append(VertexGroups)
	
	ArmObjs = []
	for i in range(0,len(OBVertGroups)):
		for arms in armatures:
			armobj = A.Get(arms)
			for j in range(0,len(OBVertGroups[i])):
				vertgroup = OBVertGroups[i]
				if vertgroup[j] in armobj.bones.keys() and len(ArmObjs) < i+1:
					#print arms 
					ArmObjs.append(arms)
	
	for i in range(0,len(OBVertGroups)):
		obj = Object.Get(objectsdata[i]['name'])
		mesh = obj.getData()
		assignment = boneass[i]
		
		for vg in OBVertGroups[i]:
			mesh.addVertGroup(vg)
		
		for j in range(0,len(assignment)):
			groupname = vertgroups[assignment[j][0]]
			if groupname in OBVertGroups[i]:
				mesh.assignVertsToGroup(groupname,assignment[j][1],assignment[j][2],'replace')
	
	for i in range(0,len(ArmObjs)):
		armobj = Object.Get(ArmObjs[i])
		meshobj = Object.Get(objectsdata[i]['name'])
		armobj.makeParentDeform([meshobj],1,0)
	
#################################################
#												#
#		Getting the Actions						#
#												#
#################################################

def getActions(lines):
	animations = []
	animation =[]
	bonetracks = []
	bonetrack = []
	keyframes = []
	keyframe = []
	rotation = []
	kfswitch = 0

	for line in lines:
	
		if '<animation name' in line:
			a1 = line.find('name="')
			a2 = line.find('length="')
			a3 = line.find('">')
			anilength = float(line[a2+8:a3])
			animation.append(line[a1+6:a2-2])
			animation.append(int(anilength*24))
	
		if '<track bone' in line:
			t1 = line.find('bone="')
			t2 = line.find('">')
			trackname = line[t1+6:t2]
			if len(trackname) > 18:
				cutter = len(trackname)-18
			else:
				cutter = 0
			bonetrack.append(trackname[+cutter:])
			
		if '<keyframe time' in line:
			kfswitch = 1
			kt1 = line.find('time="')
			kt2 = line.find('">')
			kftime = float(line[kt1+6:kt2])
			keyframe.append(int(kftime*24))
			
		if '<translate x' in line and kfswitch == 1:
			t1 = line.find('x="')
			t2 = line.find('y="')
			t3 = line.find('z="')
			t4 = line.find('/>')
			x = float(line[t1+3:t2-2])
			y = float(line[t2+3:t3-2])
			z = float(line[t3+3:t4-2])
			trans = [x,y,z]
			keyframe.append(trans)
			
		if '<rotate angle' in line and kfswitch == 1:
			ag1 = line.find('angle="')
			ag2 = line.find('">')
			angle = float(line[ag1+7:ag2])
			rotation.append(angle)
			
		if '<axis' in line and kfswitch == 1:
			ax1 = line.find('x="')
			ax2 = line.find('y="')
			ax3 = line.find('z="')
			ax4 = line.find('/>')
			x = float(line[ax1+3:ax2-2])
			y = float(line[ax2+3:ax3-2])
			z = float(line[ax3+3:ax4-2])
			rotation.append(x)
			rotation.append(y)
			rotation.append(z)
			keyframe.append(rotation)
			rotation = []
			
		if '</keyframe>' in line:
			keyframes.append(keyframe)
			keyframe = []
			kfswitch = 0
		
		if '</keyframes>' in line:
			bonetrack.append(keyframes)
			keyframes = []
		
		if '</track>' in line:
			bonetracks.append(bonetrack)
			bonetrack = []
			
		if '</tracks>' in line:
			animation.append(bonetracks)
			bonetracks = []
	
		if '</animation>' in line:
			animations.append(animation)
			animation = []
			
	return animations



#################################################
#												#
#	Creating the Actions						#
#												#
#################################################
# WIP											#
#################################################

def createActions(actions,armatures):
	counter = 0
	global sf
	for armature in armatures:
		armobj = Object.Get(armature)
		pose = armobj.getPose()
		armdata = armobj.getData()
		rootbone = armdata.bones['Root']
		rootbonechildren = rootbone.children
		rootchildlist = []
		for child in rootbonechildren:
			rootchildlist.append(child.name)
		
	
								
		for action in actions:
			newaction = A.NLA.NewAction(str(counter)+action[0])
			newaction.setActive(armobj)
			
			
			for tracks in action[2]:
				
				if tracks[0] in pose.bones.keys():
					pbone = pose.bones[tracks[0]]
					
																				
					for kfrs in tracks[1]:
						
						frame = kfrs[0]+1
						
						angle = kfrs[2][0]
						axis = Vector(kfrs[2][1],kfrs[2][3],-kfrs[2][2])
						quat = Quaternion(axis,degrees(angle))
						pbone.quat = Quaternion(axis,degrees(angle))				
						
						pbone.insertKey(armobj,frame,[Object.Pose.ROT])
				
				if tracks[0] in rootchildlist:
					pbone = pose.bones['Root']
					for kfrs in tracks[1]:
						frame = kfrs[0]+1
						pbone.loc = Vector(kfrs[1][0]*sf,-kfrs[1][2]*sf,kfrs[1][1]*sf)
						pbone.insertKey(armobj,frame,[Object.Pose.LOC])
				
						
					
							
			
		counter += 1

	
#################################################
#												#
#	Mesh file Converter							#
#												#
#################################################

def convert_meshfile(filename):
	global OGREXMLCONVERTER
	if OGREXMLCONVERTER != '':
		commandline = OGREXMLCONVERTER + " " + filename
		print "try to convert meshfile"
		os.system(commandline)
		


#################################################
# 												#
#	Main Fuction 								#
#												#
#################################################	
		
def fileselection(filename2):
	global impact	
	
	print filename2
	if (filename2.lower().find('.xml') == -1):
		convert_meshfile(filename2)
		filename2 += '.xml'
	
	filein = open(filename2)
	
	zeilen = filein.readlines()
	
	dirname = sys.dirname(filename2)
	
	basename = sys.basename(filename2)
	
	FileName = basename[0:basename.lower().find('.mesh.xml')]

	
	
	print filename2,dirname
	createMesh(zeilen,dirname)

	filein.close()

	skfile = getSkeletonFile(zeilen)
	
	sk = 0
	if skfile != None:
		try:
			filein = open(dirname+"/"+skfile+".xml","r")
				
		except:
			print "no .skeleton.xml file found"
			sk = 1
		
		else:
			sk = 0
			print dirname+"/"+skfile+".xml"
			data = filein.readlines()

			filein.close()
			createEmpties(data)
			armatures = createArmature(getArmatureBones(data),FileName)
			setBoneMatrices(armatures)
			
	
	if sk == 1:
		try:
			convert_meshfile(dirname+"/"+skfile)
			
		except:
			print "no skeleton file found"
			
		else:
			skfile += ".xml"
			sk = 2
	
	if sk == 2:
		filein = open(dirname+"/"+skfile,"r")
		data = filein.readlines()
		filein.close()
		createEmpties(data)
		armatures = createArmature(getArmatureBones(data),FileName)
		setBoneMatrices(armatures)
		

		

	if skfile != None:
		try:
			createVertGroups(data,zeilen,armatures)
		except:
			print "no armature imported"
			
		if impact == 1:
			animations = getActions(data)
		
			if animations != None:
				createActions(animations,armatures)
				
	
		
	

########################################################
#													   #
#			Graphical User Interface				   #
#													   #
########################################################


def fileselection1(filename):
	global OGREXMLCONVERTER,Textbox1
	Textbox1 = filename
	OGREXMLCONVERTER = filename

def fileselection2(filename):
	global MeshFile,Textbox2
	Textbox2 = filename
	MeshFile = filename
	
	
def draw():
	global convsv, convsel, Textbox1, Textbox2, scale
	global impact, acttext, sf

	
	
	glClearColor(0.753, 0.753, 0.753, 0.0)
	glClear(GL_COLOR_BUFFER_BIT)
	Draw.Toggle(acttext,1,32,335,170,15,impact,'')
	
	glRasterPos2i(32,253)
	Draw.Text('Scale Factor:')
	scale = Draw.Number('', 2, 122, 250, 90, 15, sf*100, 0, 1000, '')
	glRasterPos2i(222,253)
	Draw.Text('%')
	
	glRasterPos2i(32,220)
	Draw.Text('Select your ".mesh" /".mesh.xml" file:')
	Draw.String('',3,32,195,319,15, Textbox2, 399, '')
	Draw.Button('Select File',4,352,195,83,15)

		
		
	glRasterPos2i(32,150)
	Draw.Text('Path to your OgreXMLConverter:')
	Draw.String('', 5, 32, 125, 319, 15, Textbox1, 399, '')
	Draw.Button('Select', 6, 352, 125, 63, 15, '')
	Draw.Button('Save Path', 7, 416, 125, 63, 15, '')

	
	
	Draw.Button('OK',8,32,50,90,30,'')
	Draw.Button('Exit',9,340,50,90,30,'')
	





def event(evt, val):
	if (evt== Draw.QKEY and not val): Draw.Exit()
		

def bevent(evt):
	global OGREXMLCONVERTER, Textbox1, Textbox2, scale
	global impact, acttext, sf
	
	if evt == 1:
		impact = 1-impact
		if impact == 1:
			acttext = 'Import Actions'
		if impact == 0:
			acttext = 'do not import Actions'
		Draw.Redraw(1)
		
	elif evt == 2:
		sf = scale.val/100
		
		
	elif evt == 4:
		Window.FileSelector(fileselection2,'Select','*.mesh, *.mesh.xml')
		
		
	elif evt == 6: 
		Window.FileSelector(fileselection1,'ConverterPath','')
		
			
			
	elif evt == 7: 
		print "save settings"
		settfile = open('OGRE3DImportSettings.ini','w')
		settfile.write(OGREXMLCONVERTER)
		settfile.flush()
		settfile.close()
		
	elif evt == 8:
		filename = MeshFile
		fileselection(filename)
		return

	
		
		
	elif evt == 9:
		Draw.Exit()
		return



####----Main Program----####

	
try: 
	OGREXMLCONVERTER = open('OGRE3DImportSettings.ini','r').read()
except: 
	OGREXMLCONVERTER = ''


Textbox1 = OGREXMLCONVERTER
Textbox2 = ''
sf = 0.25
scale = Draw.Create(25.0)
impact = 0
acttext = 'do not import Actions'	
				
	
	

Draw.Register(draw, event, bevent)