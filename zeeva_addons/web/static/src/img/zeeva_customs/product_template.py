# -*- coding: utf-8 -*-

import math
import Image
import base64

from osv import fields,osv
import tools
import pooler
from tools.translate import _

import time

import openerp.addons.decimal_precision as dp

RANGE_EARPHONES = [ 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129,
                    130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159,
                    160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189,
                    190, 191, 192, 193, 194, 195, 196, 197, 198, 199 ]
                    
RANGE_HEADPHONES = [ 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 
                     230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 
                     260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 
                     290, 291, 292, 293, 294, 295, 296, 297, 298, 299 ]
                     
RANGE_SPEAKERS = [ 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 
                   330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359, 
                   360, 361, 362, 363, 364, 365, 366, 367, 368, 369, 370, 371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 
                   390, 391, 392, 393, 394, 395, 396, 397, 398, 399 ]

RANGE_OTHERS = [ 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129,
                130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159,
                160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189,
                190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 
                220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 
                250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 
                280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 
                310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 
                340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364, 365, 366, 367, 368, 369, 
                370, 371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 396, 397, 398, 399,
                1000, 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010, 1011, 1012, 1013, 1014, 1015, 1016, 1017, 1018, 1019, 
                1020, 1021, 1022, 1023, 1024, 1025, 1026, 1027, 1028, 1029, 1030, 1031, 1032, 1033, 1034, 1035, 1036, 1037, 1038, 1039,
                1040, 1041, 1042, 1043, 1044, 1045, 1046, 1047, 1048, 1049 ]

RANGE_SERVICES = [ 1000, 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010, 1011, 1012, 1013, 1014, 1015, 1016, 1017, 1018, 1019, 
                   1020, 1021, 1022, 1023, 1024, 1025, 1026, 1027, 1028, 1029, 1030, 1031, 1032, 1033, 1034, 1035, 1036, 1037, 1038, 1039,
                   1040, 1041, 1042, 1043, 1044, 1045, 1046, 1047, 1048, 1049 ]

class product_template(osv.osv):
    _inherit = ['product.template','mail.thread']
    _name = 'product.template'
    
    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image, avoid_resize_medium=True)
        return result

    def _set_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, context=context)
        
    _columns = {
        'description': fields.text('Description',translate=False),
        'name_categ': fields.related('categ_id', 'name', string="Name", type='char', size=128, store=True),
        #'is_multi_variants' : fields.boolean('Is Multi Variants?', help="Determines if the Raw product can be used to create client variants."),
        #'zeeva_raw_code': fields.char('Code',size=64),
        #'name': fields.char('Code',size=64, translate=False),
        
        'state': fields.selection([
            ('design', 'Design development'),
            ('prototype', 'Prototype development'),
            ('tooling', 'Tooling development'),
            ('sellable','Ready for mass production'),
            ('obsolete','Obsolete')], 'Status', track_visibility='onchange', help="Tells the user if he can use the product or not."),
            
        'zeeva_categ_seq': fields.integer('Cat. seq. nb'),
        
        'raw_creation_user': fields.many2one('res.users','Created by'),
        'raw_creation_date': fields.date('Created on'),
        
        'raw_reqapproval_flag': fields.boolean('Approval request sent'),
        'raw_reqapproval_user': fields.many2one('res.users','Approval request by'),
        'raw_reqapproval_date': fields.date('Approval request on'),
        
        'raw_approval_flag': fields.boolean('Raw product approved'),
        'raw_approval_user': fields.many2one('res.users','Approved by'),
        'raw_approval_date': fields.date('Approved on'),
        
        #'zeeva_raw_thumbnail': fields.binary('Raw Image'),
        #'zeeva_raw_image1': fields.binary('Raw Image'),
        #'zeeva_raw_image2': fields.binary('Raw Image'),
        
        # image: all image fields are base64 encoded and PIL-supported
        'image': fields.binary("Image",
            help="Raw product - full image"),
        'image_medium': fields.binary("Image for Spec.Sheet report",
            help="Raw product - medium size image with a fixed size of 90*70px"),
        'image_small': fields.binary("Small-size Image",
            help="Raw product - small size image with a width of 64px"),
        #'image_medium': fields.function(_get_image, fnct_inv=_set_image,
            #string="Medium-sized image", type="binary", multi="_get_image",
            #store={
                #'product.template': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            #},
            #help="Medium-sized image of the product. It is automatically "\
                 #"resized as a 128x128px image, with aspect ratio preserved, "\
                 #"only when the image exceeds one of those sizes. Use this field in form views or some kanban views."),
        #'image_small': fields.function(_get_image, fnct_inv=_set_image,
            #string="Small-sized image", type="binary", multi="_get_image",
            #store={
                #'product.template': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            #},
            #help="Small-sized image of the product. It is automatically "\
                 #"resized as a 64x64px image, with aspect ratio preserved. "\
                 #"Use this field anywhere a small image is required."),
        
        'image_ids': fields.one2many('product.zeemage', 'product_tmpl_id', 'Product images'),
        
    #=== EARPHONES
        'earphone_impedance': fields.selection([('16','16 Ohms'),
                                                ('32','32 Ohms')], 'Impedance'),
        'earphone_freq_min': fields.integer('Frequency min'),
        'earphone_freq_max': fields.integer('Frequency max'),
        'earphone_sensitivity': fields.selection([('96','96 dB'),
                                                  ('100','100 dB'),
                                                  ('102','102 dB'),
                                                  ('110','110 dB')], 'Sensitivity'),
        'earphone_material': fields.selection([('plastic','Plastic'), ('metal','Metal')], 'Material'),
        'earphone_driver_diam': fields.selection([('6','6 mm'),
                                                  ('7','7 mm'),
                                                  ('8','8 mm'),
                                                  ('9','9 mm'),
                                                  ('10','10 mm'),
                                                  ('13','13 mm'),
                                                  ('15','15 mm')], 'Driver Diameter'),                                 
        #'earphone_driver_type': fields.char('Driver Type',size=128),
        'earphone_driver_type': fields.selection([('dynamic','Dynamic')], 'Driver Type'),
        'earphone_cord_length': fields.float('Cord Length', digits=(12, 1)),
        'earphone_cord_type': fields.char('Cord Type',size=128),
        'earphone_cord_addons': fields.selection([('no','None'),
                                                  ('mic','Microphone'),
                                                  ('vol','Volume control'),
                                                  ('both','Volume control + Mic.')], 'Cord Add Ons'),                          
        'earphone_plug_type': fields.selection([('no','None'),
                                                ('lsh','L-shaped'),
                                                ('ssh','Straight-shaped')], 'Plug Type'),
        'earphone_plug_plating': fields.selection([('gplated','Gold plated'),
                                                   ('gcoated','Gold coated'),
                                                   ('nplated','Nickel plated')], 'Plug Plating'),
        
    #=== HEADPHONES
        'headphone_impedance': fields.selection([('16','16 Ohms'),
                                                ('32','32 Ohms')], 'Impedance'),
        'headphone_freq_min': fields.integer('Frequency min'),
        'headphone_freq_max': fields.integer('Frequency max'),
        'headphone_sensitivity': fields.selection([('85','85 dB'),
                                                   ('96','96 dB'),
                                                   ('100','100 dB'),
                                                   ('102','102 dB'),
                                                   ('110','110 dB')], 'Sensitivity'),
        'headphone_band_mat1': fields.selection([('plastic','Plastic'),('metal','Metal'),('leather','Leather'),('pu','PU Leather')], 'Headband Material'),
        'headphone_band_mat2': fields.selection([('plastic','Plastic'),('metal','Metal'),('leather','Leather'),('pu','PU Leather')], 'Headband Material'),
        'headphone_joint_mat1': fields.selection([('plastic','Plastic'),('metal','Metal'),('leather','Leather'),('pu','PU Leather')], 'Mechanical Joints Material'),
        'headphone_joint_mat2': fields.selection([('plastic','Plastic'),('metal','Metal'),('leather','Leather'),('pu','PU Leather')], 'Mechanical Joints Material'),
        'headphone_shell_mat1': fields.selection([('plastic','Plastic'),('metal','Metal'),('leather','Leather'),('pu','PU Leather')], 'Shells Material'),
        'headphone_shell_mat2': fields.selection([('plastic','Plastic'),('metal','Metal'),('leather','Leather'),('pu','PU Leather')], 'Shells Material'),
        
        'headphone_driver_diam': fields.selection([('30','30 mm'),
                                                   ('40','40 mm'),
                                                   ('50','50 mm'),
                                                   ('57','57 mm')], 'Driver Diameter'),
        #'headphone_driver_type': fields.char('Driver Type',size=128),
        'headphone_driver_type': fields.selection([('dynamic','Dynamic')], 'Driver Type'),
        'headphone_cord_length': fields.float('Cord Length', digits=(12, 1)),
        'headphone_cord_type': fields.char('Cord Type',size=128),
        'headphone_cord_addons': fields.selection([('no','None'),
                                                  ('mic','Microphone'),
                                                  ('vol','Volume control'),
                                                  ('both','Volume control + Mic.')], 'Cord Add Ons'),                          
        'headphone_plug_type': fields.selection([('no','None'),
                                                ('lsh','L-shaped'),
                                                ('ssh','Straight-shaped')], 'Plug Type'),
        'headphone_plug_plating': fields.selection([('gplated','Gold plated'),
                                                   ('gcoated','Gold coated'),
                                                   ('nplated','Nickel plated')], 'Plug Plating'),
                                                   
    #=== SPEAKERS
        'speaker_material_body': fields.selection([('plastic','Plastic'), ('metal','Metal')], 'Body Material'),
        'speaker_material_grill': fields.selection([('plastic','Plastic'), ('metal','Metal'), ('fabric','Fabric Mesh')], 'Grill Material'),
        'speaker_driver_diam': fields.integer('Driver Diameter'),
        'speaker_driver_type': fields.selection([('dynamic','Dynamic')], 'Driver Type'),
        'speaker_type': fields.selection([('mono','Mono'), ('stereo','Stereo')], 'Speaker Type'),
        'speaker_output_power': fields.float('Output Power', digits=(12, 2)),
        'speaker_output_nb': fields.integer('No of Speakers'),
        'speaker_led_indicator': fields.selection([('yes','Yes'),
                                                    ('no','No')], 'ON/OFF LED Indicator'),
        'speaker_battery': fields.selection([('no','None'),
                                            ('3a','AAA'),
                                            ('2a','AA'),
                                            ('liion','Li-Ion')], 'Battery'),
        'speaker_battery_nb': fields.integer('Quantity'),
        'speaker_battery_capacity': fields.integer('Capacity'),
        'speaker_battery_rechargeable': fields.selection([('yes','Yes'),
                                                          ('no','No')], 'Rechargeable'),
        'speaker_battery_rechargeable_type': fields.selection([('usb','USB'),
                                                               ('adaptor','Adaptor')], 'Recharge Type'),
        'speaker_ac_adaptor': fields.selection([('yes','Yes'),
                                                ('no','No')], 'AC adaptor'),
        'speaker_impedance': fields.integer('Impedance'),
        'speaker_bt': fields.selection([('yes','Yes'),
                                        ('no','No')], 'Bluetooth'),
        'speaker_bt_version': fields.char('Bluetooth Version', size=128),
        'speaker_bt_range': fields.char('Bluetooth Range', size=128),
        'speaker_bt_supplier': fields.char('Bluetooth Chip Supplier', size=128),
        'speaker_aux_connector': fields.selection([('yes','Yes'),
                                                    ('no','No')], 'AUX Connector'),
        'speaker_aux_cable_length': fields.float('AUX Cable Length', digits=(12, 1)),
        'speaker_aux_cable_type': fields.selection([('attached','Attached'),
                                                    ('detached','Detached')], 'AUX Cable Type'),
        'speaker_mic': fields.selection([('yes','Yes'),
                                        ('no','No')], 'Microphone'),
        'speaker_call_answer_button': fields.selection([('yes','Yes'),
                                                        ('no','No')], 'Call Answer Button'),
        
    #=== CASING
        #=== Phones
        'protec_phone_device': fields.selection([ ('s3','Galaxy S3'),
                                                   ('s4','Galaxy S4'),
                                                   ('i4','iPhone 3G/3GS'),
                                                   ('i4','iPhone 4/4S'),
                                                   ('i5','iPhone 5')], 'Device'),
        'protec_phone_material': fields.selection([('abs','ABS'),
                                                   ('pvc','PVC'),
                                                   ('tpu','TPU'),
                                                   ('silicon','Silicon')], 'Material'),
        'protec_phone_bumper': fields.selection([('yes','Yes'),('no','No')], 'Front Side Bumper'),
        'protec_phone_camhole': fields.selection([('yes','Yes'),('no','No')], 'Camera Hole'),
        'protec_phone_camhole_type': fields.selection([('fit','Fitted'),('large','Large')], 'Camera Hole Type'),
        'protec_phone_volume_type': fields.selection([('fit','Fitted'),('open','Open')], 'Volume Control Type'),
        'protec_phone_on_type': fields.selection([('fit','Fitted'),('open','Open')], 'On/Off Control Type'),
        
        #=== Music players
        'protec_music_device': fields.selection([ ('i5','iPod Touch 5')], 'Device'),
        
        #=== Tab Folios
        'folio_size': fields.selection([('7','7"'),('10','10"')], 'Size'),
        'folio_device': fields.char('Device type', size=128),
        'folio_material': fields.selection([('pu','Polyurethane (PU)')], 'Material'),
        'folio_attach': fields.selection([('none','None'),('magnet','Magnet'),('clip','Clip')], 'Attach/Joining'),
        'folio_protection': fields.selection([('fit','Fitted'),('strap','Straps')], 'Protection Type'),
        'folio_camhole': fields.selection([('yes','Yes'),('no','No')], 'Camera Hole'),
        'folio_stylus': fields.selection([('yes','Yes'),('no','No')], 'Stylus Holder'),
        'folio_functionalities': fields.selection([('none','None'),('folding','Folding')], 'Functionalities'),
        
        #=== Tab Sleeves
        'sleeve_size': fields.selection([('7','7"'),('10','10"')], 'Size'),
        'sleeve_device': fields.char('Device type', size=128),
        'sleeve_material': fields.selection([   ('np','Neoprene'),
                                                ('pu','PU Leather')], 'Material'),
        'sleeve_zipper': fields.selection([('1','1 Side'),('2','2 Sides')], 'Zipper'),
        'sleeve_zipper_type': fields.selection([('general','General'),('specific','Specific')], 'Zipper Type'),
        'sleeve_pocket': fields.selection([('yes','Yes'),('no','No')], 'Pocket'),
        'sleeve_pocket_type': fields.selection([('single','Single Opening'),('double','Double Opening')], 'Pocket Type'),
        
    #=== CHARGERS
        
    #=== POWER BANK
        
    #=== SCREEN PROTECTOR
        
    #=== OTHERS
        
    }
    
    _order = "name"
    
    _defaults = {
        #'is_multi_variants' : lambda * a: True,
        'name': '/',
        'state': 'design',
        'type': 'product',
        'procure_method': 'make_to_order',
        #'sale_ok': False,
        #'purchase_ok': False,
    }
    
    #def print_size(self, cr, uid, ids, context=None):
        
        #for obj in self.browse(cr, uid, ids, context=context):
            #print "Image: ", len(obj.image or '')
            #print "Image small: ", len(obj.image_small or '')
            #print "Image medium: ", len(obj.image_medium or '')
            
        #return True
    
    def onchange_ref(self, cr, uid, ids, categ_id, context=None):
        result = {}
        code = 0
        name = ""
        
        if categ_id:
            categ_obj = self.pool.get('product.category').browse(cr, uid, categ_id, context=None)
            code = categ_obj.sequence
            
        result = {'value': {'zeeva_categ_seq': code}}
        
        return result
        
    def create(self, cr, user, vals, context=None):
        
        # Get the next name
        if ('name' not in vals) or (vals.get('name')=='/'):
            if ('categ_id' in vals):
                categ_obj = self.pool.get('product.category').browse(cr, user, vals['categ_id'], context=None)
                seq = categ_obj.sequence
                if seq in range(100,200):
                    vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'product.template.earphones')
                elif seq in range(200,300):
                    vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'product.template.headphones')
                elif seq in range(300,400):
                    vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'product.template.speakers')
                elif seq in [401,402]:
                    vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'product.template.casing')
                elif seq == 403:
                    vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'product.template.folio')
                elif seq == 404:
                    vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'product.template.sleeve')
                elif seq == 425:
                    vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'product.template.screenprotec')
                elif seq in range(400,450):
                    vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'product.template.others')
                elif seq == 450:
                    vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'product.template.chargers')
                elif seq == 475:
                    vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'product.template.powerbank')
                elif seq in range(451,1000):
                    vals['name'] = self.pool.get('ir.sequence').get(cr, user, 'product.template.others')
                else:
                    #print vals
                    pass
        #print vals
        
        vals['raw_creation_user'] = user
        vals['raw_creation_date'] = fields.date.context_today(self,cr,user,context=context)

        return super(product_template,self).create(cr, user, vals, context)
        
    def copy(self, cr, uid, id, default=None, context=None):
        if context is None:
            context={}

        if not default:
            default = {}
        default = default.copy()
        
        # Get the next name
        seq = 0
        tmpl_obj = self.browse(cr, uid, id, context=None)
        if tmpl_obj.categ_id:
            categ_obj = self.pool.get('product.category').browse(cr, uid, tmpl_obj.categ_id.id, context=None)
            seq = categ_obj.sequence
        if seq in range(100,200):
            name = self.pool.get('ir.sequence').get(cr, uid, 'product.template.earphones')
        elif seq in range(200,300):
            name = self.pool.get('ir.sequence').get(cr, uid, 'product.template.headphones')
        elif seq in range(300,400):
            name = self.pool.get('ir.sequence').get(cr, uid, 'product.template.speakers')
        elif seq in [401,402]:
            name = self.pool.get('ir.sequence').get(cr, uid, 'product.template.casing')
        elif seq == 403:
            name = self.pool.get('ir.sequence').get(cr, uid, 'product.template.folio')
        elif seq == 404:
            name = self.pool.get('ir.sequence').get(cr, uid, 'product.template.sleeve')
        elif seq == 425:
            name = self.pool.get('ir.sequence').get(cr, uid, 'product.template.screenprotec')
        elif seq in range(400,450):
            name = self.pool.get('ir.sequence').get(cr, uid, 'product.template.others')
        elif seq == 450:
            name = self.pool.get('ir.sequence').get(cr, uid, 'product.template.chargers')
        elif seq == 475:
            name = self.pool.get('ir.sequence').get(cr, uid, 'product.template.powerbank')
        elif seq in range(451,1000):
            name = self.pool.get('ir.sequence').get(cr, uid, 'product.template.others')
        else:
            name = self.browse(cr, uid, id, context=None).name
                    
        default.update({
            'name': name,
            'state': 'design',
            'raw_approval_flag': False,
            'raw_approval_user': False,
            'raw_approval_date': False,
            'raw_creation_user': uid,
            'raw_creation_date': fields.date.context_today(self,cr,uid,context=context),
            'raw_reqapproval_flag': False,
            'raw_reqapproval_user': False,
            'raw_reqapproval_date': False,
            'image': False,
            'image_small': False,
            'image_medium': False,
        })
                
        return super(product_template, self).copy(cr, uid, id, default=default, context=context)
        
    #def copy(self, cr, uid, id, default=None, context=None):
        #if default is None:
            #default = {}
        #default = default.copy()
        #default.update({'name':'toto', })
        #return super(product_template, self).copy(cr, uid, id, default, context)
    
    #def generate_thumbnail(self, cr, uid, ids, context=None):
        #product_obj = self.pool.get('product.template').browse(cr, uid, ids, context=None)
        
        #im_original = product_obj[0].zeeva_raw_image1

        #if product_obj:
            #product_obj[0].write({'zeeva_raw_thumbnail': im_original})
        
        #return True
        
    #def message_subscribe_users(self, cr, uid, ids, context=None):
        #sub_ids = self.message_subscribe_users(cr, uid, ids, context=context);
        #print "toto\n"
        #return sub_ids
        
    def message_subscribe_users(self, cr, uid, ids, user_ids=None, subtype_ids=None, context=None):
        """ Wrapper on message_subscribe, using users. If user_ids is not
            provided, subscribe uid instead. """
            
        if user_ids is None:
            user_ids = [uid]
            
        #ZEEVA mod start 2013-03-18
            #TODO auto add bosses by group instead of name to allow future external user to approve a product
        boss_id = self.pool.get('res.users').search(cr, uid, ['|',('login','=','akshay'),('login','=','nitin')])
        user_ids += boss_id
        #ZEEVA mod stop 2013-03-18
        
        partner_ids = [user.partner_id.id for user in self.pool.get('res.users').browse(cr, uid, user_ids, context=context)]
        return self.message_subscribe(cr, uid, ids, partner_ids, subtype_ids=subtype_ids, context=context)
        
    # Check if at least one of each image type in vals is in the list of image ids
    def zeeva_product_image_check(self, cr, uid, ids, vals, product_type, context=None):
        #print ids
        #print vals
        mis_images = []
        
        if product_type == 'earphone':
            for im_type in vals:
                flag = False
                
                for image in ids:
                    if im_type == image.view_type_earphone: flag = True
                    
                if not flag: # No image found of type "im_type"
                    mis_images += [im_type]
                    
        elif product_type == 'headphone':
            for im_type in vals:
                flag = False
                
                for image in ids:
                    if im_type == image.view_type_headphone: flag = True
                    
                if not flag: # No image found of type "im_type"
                    mis_images += [im_type]
            
        elif product_type == 'speaker':
            for im_type in vals:
                flag = False
                
                for image in ids:
                    if im_type == image.view_type_speaker: flag = True
                    
                if not flag: # No image found of type "im_type"
                    mis_images += [im_type]
                    
        else:
            True
                
        # Formating the return list
        result = ''
        for name in mis_images:
            if   name == 'a1_catalog':  result += 'Catalog image, '
            elif name == 'b1_front':    result += 'Front view, '
            elif name == 'b2_back' :    result += 'Back view, '
            elif name == 'c1_left' :    result += 'Left side view, '
            elif name == 'c2_right':    result += 'Right side view, '
            elif name == 'c3_side' :    result += 'Side view, '
            elif name == 'd1_top'  :    result += 'Top view, '
            elif name == 'd2_bottom':   result += 'Bottom view, '
            elif name == 'e1_three':    result += 'Three-quarter view, '
            elif name == 'f1_plug':     result += 'Plug view, '
            elif name == 'f2_cable':    result += 'Cable view, '
            elif name == 'f3_button':   result += 'Buttons view, '
            elif name == 'f4_grill':    result += 'Grill view, '
            elif name == 'g1_addons':   result += 'Add-ons view, '
            elif name == 'h1_access':   result += 'Product accessories view, '
            elif name == 'i1_pos':      result += 'Product position in package view, '
            elif name == 'j1_pfront':   result += 'Package front view, '
            elif name == 'j2_pback':    result += 'Package back view, '
                
        return result        
        
    
    # Request for product approval from Management
    def zeeva_reqapprove_raw(self, cr, uid, ids, context=None):
        product_obj = self.pool.get('product.template').browse(cr, uid, ids, context=None)
        warning = {}
        
        if product_obj:
                
            ### Check if there is at least one supplier defined
            if product_obj[0].zeeva_categ_seq in range(100,900):
                if product_obj[0].seller_ids == []:
                    raise osv.except_osv(   _('Supplier not defined!'),
                                            _('You must define at least one supplier.'))
            
            ### Check if all required images are present
            req_images = [] # required views
            mis_images = '' # missing views
            mis_fields = ''
            
            #========================================================================================================
            # CHECK EARPHONES FIELDS
            if product_obj[0].zeeva_categ_seq in range(100,200):
                
                #1: Required images
                req_images = ['a1_catalog','b1_front','c3_side']
                
                if product_obj[0].earphone_plug_type not in ['no',False]:
                    req_images += ['f1_plug']
                if product_obj[0].earphone_cord_addons not in ['no',False]:
                    req_images += ['g1_addons']
                
                # Then check the images of the raw product
                mis_images = self.zeeva_product_image_check(cr, uid, product_obj[0].image_ids, req_images, 'earphone')
                
                #2: Characteristics fields
                if product_obj[0].earphone_impedance == False:
                    mis_fields += 'Impedance, '
                if product_obj[0].earphone_freq_min == 0:
                    mis_fields += 'Frequency min, '
                if product_obj[0].earphone_freq_max == 0:
                    mis_fields += 'Frequency max, '
                if product_obj[0].earphone_sensitivity == False:
                    mis_fields += 'Sensitivity, '
                if product_obj[0].earphone_material == False:
                    mis_fields += 'Material, '
                if product_obj[0].earphone_driver_diam == False:                                
                    mis_fields += 'Driver Diameter, '
                if product_obj[0].earphone_driver_type == False:
                    mis_fields += 'Driver Type, '
                if product_obj[0].earphone_cord_length == 0.0:
                    mis_fields += 'Cord Length, '
                if product_obj[0].earphone_cord_type == False:
                    mis_fields += 'Cord Type, '
                if product_obj[0].earphone_cord_addons == False:
                    mis_fields += 'Cord Add-ons, '
                if product_obj[0].earphone_plug_type == False:
                    mis_fields += 'Plug Type, '
                if product_obj[0].earphone_plug_plating == False:
                    mis_fields += 'Plug Plating, '
                
            #========================================================================================================
            # CHECK HEADPHONES FIELDS
            elif product_obj[0].zeeva_categ_seq in range(200,300):
                
                #1: Required images
                req_images = ['a1_catalog','b1_front','c3_side']
                
                if product_obj[0].headphone_plug_type not in ['no',False]:
                    req_images += ['f1_plug']
                if product_obj[0].headphone_cord_addons not in ['no',False]:
                    req_images += ['g1_addons']
                
                # Then check the images of the raw product
                mis_images = self.zeeva_product_image_check(cr, uid, product_obj[0].image_ids, req_images, 'headphone')
                
                #2: Required fields
                if product_obj[0].headphone_impedance == False:
                    mis_fields += 'Impedance, '
                if product_obj[0].headphone_freq_min == 0:
                    mis_fields += 'Frequency min, '
                if product_obj[0].headphone_freq_max == 0:
                    mis_fields += 'Frequency max, '
                if product_obj[0].headphone_sensitivity == False:
                    mis_fields += 'Sensitivity, , '
                if product_obj[0].headphone_band_mat1 == False:
                    mis_fields += 'Headband Material, '
                if product_obj[0].headphone_joint_mat1 == False:
                    mis_fields += 'Joints Material, '
                if product_obj[0].headphone_shell_mat1 == False:
                    mis_fields += 'Shells Material, '
                if product_obj[0].headphone_driver_diam == False:                                
                    mis_fields += 'Driver Diameter, '
                if product_obj[0].headphone_driver_type == False:
                    mis_fields += 'Driver Type, '
                if product_obj[0].headphone_cord_length == 0.0:
                    mis_fields += 'Cord Length, '
                if product_obj[0].headphone_cord_type == False:
                    mis_fields += 'Cord Type, '
                if product_obj[0].headphone_cord_addons == False:
                    mis_fields += 'Cord Add-ons, '
                if product_obj[0].headphone_plug_type == False:
                    mis_fields += 'Plug Type, '
                if product_obj[0].headphone_plug_plating == False:
                    mis_fields += 'Plug Plating, '
            
            #========================================================================================================
            # CHECK SPEAKER FIELDS
            elif product_obj[0].zeeva_categ_seq in range(300,400):
                
                #1: Required images
                req_images = ['a1_catalog','b1_front','c3_side','d1_top']
                
                if product_obj[0].speaker_call_answer_button not in ['no',False]:
                    req_images += ['f3_button']
                if product_obj[0].speaker_aux_connector not in ['no',False]:
                    req_images += ['f2_cable']
                
                # Then check the images of the raw product
                mis_images = self.zeeva_product_image_check(cr, uid, product_obj[0].image_ids, req_images, 'speaker')
                
                #2: Required fields
                if product_obj[0].speaker_material_body == False:
                    mis_fields += 'Body Material, '
                if product_obj[0].speaker_material_grill == False:
                    mis_fields += 'Grill Material, '
                if product_obj[0].speaker_driver_diam == 0:
                    mis_fields += 'Driver Diameter, '
                if product_obj[0].speaker_driver_type == False:
                    mis_fields += 'Driver Type, '
                if product_obj[0].speaker_type == False:
                    mis_fields += 'Speaker Type, '
                if product_obj[0].speaker_output_power == 0.0:
                    mis_fields += 'Output Power, '
                if product_obj[0].speaker_output_nb == 0:
                    mis_fields += 'No of Speakers, '
                if product_obj[0].speaker_led_indicator == False:
                    mis_fields += 'ON/OFF LED Indicator, '
                if product_obj[0].speaker_battery == False:
                    mis_fields += 'Battery, '
                if product_obj[0].speaker_battery in ['3a','2a'] and product_obj[0].speaker_battery_nb == 0:
                    mis_fields += 'Quantity, '
                if product_obj[0].speaker_battery in ['liion'] and product_obj[0].speaker_battery_capacity == 0:
                    mis_fields += 'Capacity, '
                if product_obj[0].speaker_battery_rechargeable == False:
                    mis_fields += 'Rechargeable, '
                if product_obj[0].speaker_battery_rechargeable == 'yes' and product_obj[0].speaker_battery_rechargeable_type == False:
                    mis_fields += 'Recharge Type, '
                if product_obj[0].speaker_ac_adaptor == False:
                    mis_fields += 'AC adaptor, '
                if product_obj[0].speaker_impedance == 0:
                    mis_fields += 'Impedance, '
                #if product_obj[0].speaker_bt == False:
                    #mis_fields += 'Bluetooth, '
                if product_obj[0].speaker_bt == 'yes' and product_obj[0].speaker_bt_version == False:
                    mis_fields += 'Bluetooth Version, '
                if product_obj[0].speaker_bt == 'yes' and product_obj[0].speaker_bt_range == False:
                    mis_fields += 'Bluetooth Range, '
                if product_obj[0].speaker_bt == 'yes' and product_obj[0].speaker_bt_supplier == False:
                    mis_fields += 'Bluetooth Chip Supplier, '
                if product_obj[0].speaker_aux_connector == False:
                    mis_fields += 'AUX Connector, '
                if product_obj[0].speaker_aux_cable_length == 0.0:
                    mis_fields += 'AUX Cable Length, '
                if product_obj[0].speaker_aux_cable_type == False:
                    mis_fields += 'AUX Cable Type, '
                if product_obj[0].speaker_mic == False:
                    mis_fields += 'Microphone, '
                if product_obj[0].speaker_call_answer_button == False:
                    mis_fields += 'Call Answer Button, '
            
            #========================================================================================================
            # CHECK CASING FIELDS
            elif product_obj[0].zeeva_categ_seq in [401,402]:
                #1: Required images
                #TODO
                
                #2: Required fields
                #Phones
                if product_obj[0].zeeva_categ_seq == 401 and product_obj[0].protec_phone_device == False:
                    mis_fields += 'Device, '
                if product_obj[0].protec_phone_material == False:
                    mis_fields += 'Material, '
                if product_obj[0].protec_phone_bumper == False:
                    mis_fields += 'Front Side Bumper, '
                if product_obj[0].protec_phone_camhole == False:
                    mis_fields += 'Camera Hole, '
                if product_obj[0].protec_phone_camhole_type == False:
                    mis_fields += 'Camera Hole Type, '
                if product_obj[0].protec_phone_volume_type == False:
                    mis_fields += 'Volume Control Type, '
                if product_obj[0].protec_phone_on_type == False:
                    mis_fields += 'On/Off Control Type, '
                
                #Music players
                if product_obj[0].zeeva_categ_seq == 402 and product_obj[0].protec_music_device == False:
                    mis_fields += 'Device, '
                
                
            #========================================================================================================
            # CHECK FOLIO FIELDS
            elif product_obj[0].zeeva_categ_seq in [403]:
                #1: Required images
                #TODO
                
                #2: Required fields
                if product_obj[0].folio_size == False:
                    mis_fields += 'Size, '
                if product_obj[0].folio_device == False:
                    mis_fields += 'Device type, '
                if product_obj[0].folio_material == False:
                    mis_fields += 'Material, '
                if product_obj[0].folio_attach == False:
                    mis_fields += 'Attach/Joining, '
                if product_obj[0].folio_protection == False:
                    mis_fields += 'Protection Type, '
                if product_obj[0].folio_camhole == False:
                    mis_fields += 'Camera Hole, '
                if product_obj[0].folio_stylus == False:
                    mis_fields += 'Stylus Holder, '
                if product_obj[0].folio_functionalities == False:
                    mis_fields += 'Functionalities, '
                
                
            #========================================================================================================
            # CHECK SLEEVE FIELDS
            elif product_obj[0].zeeva_categ_seq in [404]:
                #1: Required images
                #TODO
                
                #2: Required fields
                if product_obj[0].sleeve_size == False:
                    mis_fields += 'Size, '
                if product_obj[0].sleeve_device == False:
                    mis_fields += 'Device type, '
                if product_obj[0].sleeve_material == False:
                    mis_fields += 'Material, '
                if product_obj[0].sleeve_zipper == False:
                    mis_fields += 'Zipper, '
                if product_obj[0].sleeve_zipper_type == False:
                    mis_fields += 'Zipper Type, '
                if product_obj[0].sleeve_pocket == False:
                    mis_fields += 'Pocket, '
                if product_obj[0].sleeve_pocket == 'yes' and product_obj[0].sleeve_pocket_type == False:
                    mis_fields += 'Pocket Type, '
                
                
            else:
                True
                        
            if mis_images == '' and mis_fields == '': # Send request for approval
                message = _("<b>Approval requested</b> for raw product %s") % (product_obj[0].name)
                #print [m.id for m in product_obj[0].message_follower_ids]
                self.message_post(cr, uid, ids, body = message, type='comment', subtype='mt_comment', context = context)
                
                product_obj[0].write({'raw_reqapproval_flag': True})
                product_obj[0].write({'raw_reqapproval_user': uid})
                product_obj[0].write({'raw_reqapproval_date': fields.date.context_today(self,cr,uid,context=context)})
            
            elif mis_images != '': # Raise error message
                raise osv.except_osv(   _('Some of the required images are missing!'),
                                        _('Missing images are: %s') % mis_images)
                                        
            elif mis_fields != '': # Raise error message
                raise osv.except_osv(   _('Some of the required fields are missing!'),
                                        _('Missing fields are: %s') % mis_fields)
                return {'warning': warning,}
        return True
    
    # Cancel the request for product approval from Management
    def zeeva_unreqapprove_raw(self, cr, uid, ids, context=None):
        product_obj = self.pool.get('product.template').browse(cr, uid, ids, context=None)

        if product_obj:
            message = _("<b>Approval request canceled</b> for raw product %s") % (product_obj[0].name)
            self.message_post(cr, uid, ids, body = message, type='comment', subtype='mt_comment', context = context)
            
            product_obj[0].write({'raw_reqapproval_flag': False})
            product_obj[0].write({'raw_reqapproval_user': uid})
            product_obj[0].write({'raw_reqapproval_date': fields.date.context_today(self,cr,uid,context=context)})
        
        return True
    
    # Approve a Raw product
    def zeeva_approve_raw(self, cr, uid, ids, context=None):
        product_obj = self.pool.get('product.template').browse(cr, uid, ids, context=None)

        if product_obj:
            message = _("Raw product %s is <b>approved</b>") % (product_obj[0].name)
            self.message_post(cr, uid, ids, body = message, type='comment', subtype='mt_comment', context = context)
            
            product_obj[0].write({'raw_approval_flag': True})
            product_obj[0].write({'raw_approval_user': uid})
            product_obj[0].write({'raw_approval_date': fields.date.context_today(self,cr,uid,context=context)})
        
        return True
        
    # Un-approve a Raw product
    def zeeva_unapprove_raw(self, cr, uid, ids, context=None):
        product_obj = self.pool.get('product.template').browse(cr, uid, ids, context=None)

        if product_obj:
            message = _("Raw product %s is <b>unapproved</b> for modification. Please note that your previous documents about this raw product might be outdated.") % (product_obj[0].name)
            self.message_post(cr, uid, ids, body = message, type='comment', subtype='mt_comment', context = context)
            
            product_obj[0].write({'raw_approval_flag': False})
            product_obj[0].write({'raw_approval_user': False})
            product_obj[0].write({'raw_approval_date': False})
        
        return True
    
    def dummy(self, cr, uid, ids, context=None):
        return True
    
    def _change_status(self, cr, uid, ids, next, *args):
        """
            go to the next status
            if next is False, go to previous status
        """
        for product in self.browse(cr, uid, ids):
            if next == True:
                if product.state == 'design':
                    self.write(cr, uid, product.id, {'state': 'prototype'})
                elif product.state == 'prototype':
                    self.write(cr, uid, product.id, {'state': 'tooling'})
                elif product.state == 'tooling':
                    self.write(cr, uid, product.id, {'state': 'sellable'})
            
            else:
                if product.state == 'sellable':
                    self.write(cr, uid, product.id, {'state': 'tooling'})
                elif product.state == 'tooling':
                    self.write(cr, uid, product.id, {'state': 'prototype'})
                elif product.state == 'prototype':
                    self.write(cr, uid, product.id, {'state': 'design'})
        return True

    def next_status(self, cr, uid, ids, *args):
        return self._change_status(cr, uid, ids, True, *args)

    def prev_status(self, cr, uid, ids, *args):
        return self._change_status(cr, uid, ids, False, *args)
        
    def set_obsolete(self, cr, uid, ids, *args):
        for product in self.browse(cr, uid, ids):
             self.write(cr, uid, product.id, {'state': 'obsolete'})
        return True
    def reset_obsolete(self, cr, uid, ids, *args):
        for product in self.browse(cr, uid, ids):
             self.write(cr, uid, product.id, {'state': 'design'})
        return True
    
product_template()


class product_product(osv.osv):
    _inherit = 'product.product'
    
    def _compute_cbm(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for p in self.browse(cr, uid, ids, context=context):
            if name == 'unit_cbm':
                res[p.id] = p.unit_l * p.unit_w * p.unit_h / 1000000
            elif name == 'pack_cbm':
                res[p.id] = p.pack_l * p.pack_w * p.pack_h / 1000000
            elif name == 'inner_cbm':
                res[p.id] = p.inner_l * p.inner_w * p.inner_h / 1000000
            elif name == 'export_cbm':
                res[p.id] = p.export_l * p.export_w * p.export_h / 1000000
            else: res[p.id] = 0
        return res
        
    def _compute_cuft(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for p in self.browse(cr, uid, ids, context=context):
            if name == 'unit_cuft':
                res[p.id] = p.unit_l * p.unit_w * p.unit_h * 35.315 / 1000000
            elif name == 'pack_cuft':
                res[p.id] = p.pack_l * p.pack_w * p.pack_h * 35.315 / 1000000
            elif name == 'inner_cuft':
                res[p.id] = p.inner_l * p.inner_w * p.inner_h * 35.315 / 1000000
            elif name == 'export_cuft':
                res[p.id] = p.export_l * p.export_w * p.export_h * 35.315 / 1000000
            else: res[p.id] = 0
        return res
    
    def _get_so_lines(self, cr, uid, ids, field_names, arg=None, context=None):
        result = {}
        
        if not ids:
            return result
            
        for id in ids:
            solines_pool = self.pool.get('sale.order.line')
            result[id] = solines_pool.search(cr, uid, [('product_id', '=', id),('state','not in',['draft','cancel'])], context=context)
        
        return result
    
    def _get_po_lines(self, cr, uid, ids, field_names, arg=None, context=None):
        result = {}
        
        if not ids:
            return result
            
        for id in ids:
            solines_pool = self.pool.get('purchase.order.line')
            result[id] = solines_pool.search(cr, uid, [('product_id', '=', id),('state','not in',['draft','cancel'])], context=context)
        
        return result
    
    _columns = {
        'zeeva_partner_id': fields.many2one('res.partner', 'Customer'),
        'zeeva_cosmetics': fields.text('Cosmetics'),
        'zeeva_others': fields.text('Others'),
        'name': fields.char('Code',size=64, translate=False),
        'color_variant': fields.char('Color Variant',size=64, translate=False),
        'product_barcode': fields.char('Product Barcode', size=24),
        'product_barcode2': fields.char('Product Barcode', size=24),
        
        'image': fields.binary("Image",
            help="Finished product - full image"),
        'image_medium': fields.binary("Image for Spec.Sheet report",
            help="Finished product - medium size image with a fixed size of 90*70px"),
        'image_small': fields.binary("Small-size Image",
            help="Finished product - small size image with a width of 64px"),
        
        'image_ids': fields.one2many('product.zeemage', 'product_product_id', 'Product images'),
        
        # SO LINES and PO LINES for showing history
        #'saleorderline_ids': fields.one2many('sale.order.line', 'product_id', 'Sales Order Lines'),
        'saleorderline_ids': fields.function(_get_so_lines, method=True, 
            type='one2many', relation='sale.order.line', string='Sales Order Lines',groups="base.group_sale_salesman"),
            
        'purchaseorderline_ids': fields.function(_get_po_lines, method=True, 
            type='one2many', relation='purchase.order.line', string='Purchase Order Lines',groups="purchase.group_purchase_user"),
        
        'finished_creation_user': fields.many2one('res.users','Created by'),
        'finished_creation_date': fields.date('Created on'),
        
    #=== EARPHONES
        'earphone_impedance': fields.selection([('16','16 Ohms'),
                                                ('32','32 Ohms')], 'Impedance'),
        'earphone_freq_min': fields.integer('Frequency min'),
        'earphone_freq_max': fields.integer('Frequency max'),
        'earphone_sensitivity': fields.selection([('96','96 dB'),
                                                  ('100','100 dB'),
                                                  ('102','102 dB'),
                                                  ('110','110 dB')], 'Sensitivity'),
        'earphone_material': fields.selection([('plastic','Plastic'), ('metal','Metal')], 'Material'),
        'earphone_driver_diam': fields.selection([('6','6 mm'),
                                                  ('7','7 mm'),
                                                  ('8','8 mm'),
                                                  ('9','9 mm'),
                                                  ('10','10 mm'),
                                                  ('13','13 mm'),
                                                  ('15','15 mm')], 'Driver Diameter'),                                 
        #'earphone_driver_type': fields.char('Driver Type',size=128),
        'earphone_driver_type': fields.selection([('dynamic','Dynamic')], 'Driver Type'),
        'earphone_cord_length': fields.float('Cord Length', digits=(12, 1)),
        'earphone_cord_type': fields.char('Cord Type',size=128),
        'earphone_cord_addons': fields.selection([('no','None'),
                                                  ('mic','Microphone'),
                                                  ('vol','Volume control'),
                                                  ('both','Volume control + Mic.')], 'Cord Add Ons'),                          
        'earphone_plug_type': fields.selection([('no','None'),
                                                ('lsh','L-shaped'),
                                                ('ssh','Straight-shaped')], 'Plug Type'),
        'earphone_plug_plating': fields.selection([('gplated','Gold plated'),
                                                   ('gcoated','Gold coated'),
                                                   ('nplated','Nickel plated')], 'Plug Plating'),
        
    #=== HEADPHONES
        'headphone_impedance': fields.selection([('16','16 Ohms'),
                                                ('32','32 Ohms')], 'Impedance'),
        'headphone_freq_min': fields.integer('Frequency min'),
        'headphone_freq_max': fields.integer('Frequency max'),
        'headphone_sensitivity': fields.selection([('85','85 dB'),
                                                   ('96','96 dB'),
                                                   ('100','100 dB'),
                                                   ('102','102 dB'),
                                                   ('110','110 dB')], 'Sensitivity'),
        'headphone_band_mat1': fields.selection([('plastic','Plastic'),('metal','Metal'),('leather','Leather'),('pu','PU Leather')], 'Headband Material'),
        'headphone_band_mat2': fields.selection([('plastic','Plastic'),('metal','Metal'),('leather','Leather'),('pu','PU Leather')], 'Headband Material'),
        'headphone_joint_mat1': fields.selection([('plastic','Plastic'),('metal','Metal'),('leather','Leather'),('pu','PU Leather')], 'Mechanical Joints Material'),
        'headphone_joint_mat2': fields.selection([('plastic','Plastic'),('metal','Metal'),('leather','Leather'),('pu','PU Leather')], 'Mechanical Joints Material'),
        'headphone_shell_mat1': fields.selection([('plastic','Plastic'),('metal','Metal'),('leather','Leather'),('pu','PU Leather')], 'Shells Material'),
        'headphone_shell_mat2': fields.selection([('plastic','Plastic'),('metal','Metal'),('leather','Leather'),('pu','PU Leather')], 'Shells Material'),
        
        'headphone_driver_diam': fields.selection([('30','30 mm'),
                                                   ('40','40 mm'),
                                                   ('50','50 mm'),
                                                   ('57','57 mm')], 'Driver Diameter'),
        #'headphone_driver_type': fields.char('Driver Type',size=128),
        'headphone_driver_type': fields.selection([('dynamic','Dynamic')], 'Driver Type'),
        'headphone_cord_length': fields.float('Cord Length', digits=(12, 1)),
        'headphone_cord_type': fields.char('Cord Type',size=128),
        'headphone_cord_addons': fields.selection([('no','None'),
                                                  ('mic','Microphone'),
                                                  ('vol','Volume control'),
                                                  ('both','Volume control + Mic.')], 'Cord Add Ons'),                          
        'headphone_plug_type': fields.selection([('no','None'),
                                                ('lsh','L-shaped'),
                                                ('ssh','Straight-shaped')], 'Plug Type'),
        'headphone_plug_plating': fields.selection([('gplated','Gold plated'),
                                                   ('gcoated','Gold coated'),
                                                   ('nplated','Nickel plated')], 'Plug Plating'),
        
    #=== SPEAKERS
        'speaker_material_body': fields.selection([('plastic','Plastic'), ('metal','Metal')], 'Body Material'),
        'speaker_material_grill': fields.selection([('plastic','Plastic'), ('metal','Metal'), ('fabric','Fabric Mesh')], 'Grill Material'),
        'speaker_driver_diam': fields.integer('Driver Diameter'),
        'speaker_driver_type': fields.selection([('dynamic','Dynamic')], 'Driver Type'),
        'speaker_type': fields.selection([('mono','Mono'), ('stereo','Stereo')], 'Speaker Type'),
        'speaker_output_power': fields.float('Output Power', digits=(12, 2)),
        'speaker_output_nb': fields.integer('No of Speakers'),
        'speaker_led_indicator': fields.selection([('yes','Yes'),
                                                    ('no','No')], 'ON/OFF LED Indicator'),
        'speaker_battery': fields.selection([('no','None'),
                                            ('3a','AAA'),
                                            ('2a','AA'),
                                            ('liion','Li-Ion')], 'Battery'),
        'speaker_battery_nb': fields.integer('Quantity'),
        'speaker_battery_capacity': fields.integer('Capacity'),
        'speaker_battery_rechargeable': fields.selection([('yes','Yes'),
                                                          ('no','No')], 'Rechargeable'),
        'speaker_battery_rechargeable_type': fields.selection([('usb','USB'),
                                                               ('adaptor','Adaptor')], 'Recharge Type'),
        'speaker_ac_adaptor': fields.selection([('yes','Yes'),
                                                ('no','No')], 'AC adaptor'),
        'speaker_impedance': fields.integer('Impedance'),
        'speaker_bt': fields.selection([('yes','Yes'),
                                        ('no','No')], 'Bluetooth'),
        'speaker_bt_version': fields.char('Bluetooth Version', size=128),
        'speaker_bt_range': fields.char('Bluetooth Range', size=128),
        'speaker_bt_supplier': fields.char('Bluetooth Chip Supplier', size=128),
        'speaker_aux_connector': fields.selection([('yes','Yes'),
                                                    ('no','No')], 'AUX Connector'),
        'speaker_aux_cable_length': fields.float('AUX Cable Length', digits=(12, 1)),
        'speaker_aux_cable_type': fields.selection([('attached','Attached'),
                                                    ('detached','Detached')], 'AUX Cable Type'),
        'speaker_mic': fields.selection([('yes','Yes'),
                                        ('no','No')], 'Microphone'),
        'speaker_call_answer_button': fields.selection([('yes','Yes'),
                                                        ('no','No')], 'Call Answer Button'),
                          
    #=== CASING
        #=== Phones
        'protec_phone_device': fields.selection([ ('s3','Galaxy S3'),
                                                   ('s4','Galaxy S4'),
                                                   ('i4','iPhone 3G/3GS'),
                                                   ('i4','iPhone 4/4S'),
                                                   ('i5','iPhone 5')], 'Device'),
        'protec_phone_material': fields.selection([ ('abs','ABS'),
                                                    ('pvc','PVC'),
                                                    ('tpu','TPU'),
                                                    ('silicon','Silicon')], 'Material'),
        'protec_phone_bumper': fields.selection([('yes','Yes'),('no','No')], 'Front Side Bumper'),
        'protec_phone_camhole': fields.selection([('yes','Yes'),('no','No')], 'Camera Hole'),
        'protec_phone_camhole_type': fields.selection([('fit','Fitted'),('large','Large')], 'Camera Hole Type'),
        'protec_phone_volume_type': fields.selection([('fit','Fitted'),('open','Open')], 'Volume Control Type'),
        'protec_phone_on_type': fields.selection([('fit','Fitted'),('open','Open')], 'On/Off Control Type'),
        
        #=== Music players
        'protec_music_device': fields.selection([ ('i5','iPod Touch 5')], 'Device'),
        
        #=== Tab Folios
        'folio_size': fields.selection([('7','7"'),('10','10"')], 'Size'),
        'folio_device': fields.char('Device type', size=128),
        'folio_material': fields.selection([('pu','Polyurethane (PU)')], 'Material'),
        'folio_attach': fields.selection([('magnet','Magnet'),('clip','Clip')], 'Attach/Joining'),
        'folio_protection': fields.selection([('fit','Fitted'),('strap','Straps')], 'Protection Type'),
        'folio_camhole': fields.selection([('yes','Yes'),('no','No')], 'Camera Hole'),
        'folio_stylus': fields.selection([('yes','Yes'),('no','No')], 'Stylus Holder'),
        'folio_functionalities': fields.selection([('folding','Folding')], 'Functionalities'),
        
        #=== Tab Sleeves
        'sleeve_size': fields.selection([('7','7"'),('10','10"')], 'Size'),
        'sleeve_device': fields.char('Device type', size=128),
        'sleeve_material': fields.selection([   ('np','Neoprene'),
                                                ('pu','PU Leather')], 'Material'),
        'sleeve_zipper': fields.selection([('1','1 Side'),('2','2 Sides')], 'Zipper'),
        'sleeve_zipper_type': fields.selection([('general','General'),('specific','Specific')], 'Zipper Type'),
        'sleeve_pocket': fields.selection([('yes','Yes'),('no','No')], 'Pocket'),
        'sleeve_pocket_type': fields.selection([('single','Single Opening'),('double','Double Opening')], 'Pocket Type'),
        
    #=== CHARGERS
        
    #=== POWER BANK
        
    #=== SCREEN PROTECTOR
        
    #=== OTHERS
    
    
    ###### COSMETICS ######
    
    #=== Earphones costemics
        'ep_housing_finish': fields.selection([ ('injection','Injection'),
                                                ('metallic','Metallic'),
                                                ('uvcoating','UV coating'),
                                                ('rubberized','Rubberized')], 'Housing finish'),
        'ep_color_ext_name': fields.char('Exterior name',size=64),
        'ep_color_ext_pant': fields.char('Exterior pantone',size=64),
        'ep_color_int_name': fields.char('Interior name',size=64),
        'ep_color_int_pant': fields.char('Interior pantone',size=64),
        'ep_color_cab_name': fields.char('Cable name',size=64),
        'ep_color_cab_pant': fields.char('Cable pantone',size=64),
        'ep_color_plu_name': fields.char('Plug name',size=64),
        'ep_color_plu_pant': fields.char('Plug pantone',size=64),
        'ep_color_cus_name': fields.char('Cushion name',size=64),
        'ep_color_cus_pant': fields.char('Cushion pantone',size=64),
        
        'ep_logo': fields.selection([('yes','Yes'),('no','No')], 'Logo'),
        'ep_logo_name': fields.char('Logo name',size=128),
        'ep_logo_position': fields.char('Logo position',size=128),
        
        'ep_printing': fields.selection([('yes','Yes'),('no','No')], 'Graphic printing'),
        'ep_printing_type': fields.selection([  ('silk','Silkscreen'),
                                                ('heat','Heat transfer'),
                                                ('water','Water transfer'),
                                                ('pad','Pad printing')], 'Graphic printing type'),
        'ep_printing_desc': fields.char('Graphic description',size=128),
        
        'ep_packaging_type': fields.selection([  ('clam','Clamshell'),
                                            ('gift','Giftbox'),
                                            ('rem','Remailer'),
                                            ('blis','Blister Card'),
                                            ('bulk','Bulk Pack'),
                                            ('win','Window Box'),
                                            ('pvc','PVC Box')], 'Packaging Type'),
        'ep_packaging_remarks': fields.text('Packaging Remarks'),
        
    #=== Headphones costemics
        'hp_color_band_upper_name': fields.char('Upperside name',size=64),
        'hp_color_band_upper_pant': fields.char('Upperside pantone',size=64),
        'hp_color_band_down_name': fields.char('Underside name',size=64),
        'hp_color_band_down_pant': fields.char('Underside pantone',size=64),
        'hp_color_joint_name': fields.char('Joints name',size=64),
        'hp_color_joint_pant': fields.char('Joints pantone',size=64),
        'hp_color_shell_name': fields.char('Shells name',size=64),
        'hp_color_shell_pant': fields.char('Shells pantone',size=64),
        'hp_color_cab_name': fields.char('Cable name',size=64),
        'hp_color_cab_pant': fields.char('Cable pantone',size=64),
        'hp_color_plu_name': fields.char('Plug name',size=64),
        'hp_color_plu_pant': fields.char('Plug pantone',size=64),
        'hp_color_cus_name': fields.char('Cushion name',size=64),
        'hp_color_cus_pant': fields.char('Cushion pantone',size=64),
        
        'hp_housing_finish': fields.selection([ ('injection','Injection'),
                                                ('metallic','Metallic'),
                                                ('uvcoating','UV coating'),
                                                ('rubberized','Rubberized')], 'Housing finish'),
        'hp_logo': fields.selection([('yes','Yes'),('no','No')], 'Logo'),
        'hp_logo_name': fields.char('Logo name 1',size=128),
        'hp_logo_position': fields.char('Logo position 1',size=128),
        'hp_logo_name2': fields.char('Logo name 2',size=128),
        'hp_logo_position2': fields.char('Logo position 2',size=128),
        
        'hp_printing': fields.selection([('yes','Yes'),('no','No')], 'Graphic printing'),
        'hp_printing_type': fields.selection([  ('silk','Silkscreen'),
                                                ('heat','Heat transfer'),
                                                ('water','Water transfer'),
                                                ('pad','Pad printing')], 'Graphic printing type'),
        'hp_printing_desc': fields.char('Graphic description',size=128),
        'hp_accent_stitching': fields.char('Accent Stitching',size=128),
        'hp_deco_addons': fields.char('Decorative Add-Ons',size=128),
        
        'hp_packaging_type': fields.selection([  ('clam','Clamshell'),
                                            ('gift','Giftbox'),
                                            ('rem','Remailer'),
                                            ('blis','Blister Card'),
                                            ('bulk','Bulk Pack'),
                                            ('win','Window Box'),
                                            ('pvc','PVC Box')], 'Packaging Type'),
        'hp_packaging_remarks': fields.text('Packaging Remarks'),
        
        
    #=== Product measurements and packing
        #'weight': fields.float('Gross Weight', digits_compute=dp.get_precision('Stock Weight'), help="The gross weight in Kg."),
        #'weight_net': fields.float('Net Weight', digits_compute=dp.get_precision('Stock Weight'), help="The net weight in Kg."),
        'unit_l': fields.float('Unit Length'),
        'unit_w': fields.float('Unit Width'),
        'unit_h': fields.float('Unit Height'),
        #'unit_gross': fields.float('Unit Gross Weight', digits_compute=dp.get_precision('Stock Weight'), help="The unit gross weight in Kg."),
        'unit_net': fields.float('Unit Net Weight', digits_compute=dp.get_precision('Stock Weight'), help="The unit net weight in Kg."),
        'unit_cbm': fields.function(_compute_cbm, string='Unit CBM', type='float', digits_compute=dp.get_precision('Product Volume')),
        'unit_cuft': fields.function(_compute_cuft, string='Unit CUFT', type='float', digits_compute=dp.get_precision('Product Volume')),
        
        'pack_l': fields.float('Package Length'),
        'pack_w': fields.float('Package Width'),
        'pack_h': fields.float('Package Height'),
        'pack_gross': fields.float('Package Gross Weight', digits_compute=dp.get_precision('Stock Weight'), help="The unit+package gross weight in Kg."),
        #'pack_net': fields.float('Package Net Weight', digits_compute=dp.get_precision('Stock Weight'), help="The unit+package net weight in Kg."),
        'pack_cbm': fields.function(_compute_cbm, string='Package CBM', type='float', digits_compute=dp.get_precision('Product Volume')),
        'pack_cuft': fields.function(_compute_cuft, string='Package CUFT', type='float', digits_compute=dp.get_precision('Product Volume')),
        
        'inner_l': fields.float('Inner Carton Length'),
        'inner_w': fields.float('Inner Carton Width'),
        'inner_h': fields.float('Inner Carton Height'),
        'inner_gross': fields.float('Inner Carton Gross Weight', digits_compute=dp.get_precision('Stock Weight'), help="The inner carton gross weight in Kg."),
        'inner_net': fields.float('Inner Carton Net Weight', digits_compute=dp.get_precision('Stock Weight'), help="The inner carton net weight in Kg."),
        'inner_cbm': fields.function(_compute_cbm, string='Inner Carton CBM', type='float', digits_compute=dp.get_precision('Product Volume')),
        'inner_cuft': fields.function(_compute_cuft, string='Inner Carton CUFT', type='float', digits_compute=dp.get_precision('Product Volume')),
        
        'export_l': fields.float('Export Carton Length'),
        'export_w': fields.float('Export Carton Width'),
        'export_h': fields.float('Export Carton Height'),
        'export_gross': fields.float('Export Carton Gross Weight', digits_compute=dp.get_precision('Stock Weight'), help="The export carton gross weight in Kg."),
        'export_net': fields.float('Export Carton Net Weight', digits_compute=dp.get_precision('Stock Weight'), help="The export carton net weight in Kg."),
        'export_cbm': fields.function(_compute_cbm, string='Export Carton CBM', type='float', digits_compute=dp.get_precision('Product Volume')),
        'export_cuft': fields.function(_compute_cuft, string='Export Carton CUFT', type='float', digits_compute=dp.get_precision('Product Volume')),
        
        'pack_inner': fields.integer('Inner Carton'),
        'pack_inner_barcode': fields.char('Inner Carton Barcode'),
        'pack_export': fields.integer('Export Carton'),
        'pack_export_barcode': fields.char('Export Carton Barcode'),
        'pack_remarks': fields.text('Additional Packing Information'),
        
        'inspection_std': fields.selection([('1','1.5 / 2.0'), ('2','1.5 / 4.0'), ('3','2.5 / 4.0')], 'Inspection Standard'),
        'inspection_remarks': fields.text('Additional Inspection Information'),
        
        'mat_rohs': fields.boolean('ROHS'),
        'mat_cpsia': fields.boolean('CPSIA'),
        'mat_prop65': fields.boolean('PROP65'),
        'mat_reach': fields.boolean('REACH'),
        'mat_en71': fields.boolean('EN71'),
        'mat_astm': fields.boolean('ASTM'),
        'mat_pahs': fields.boolean('PAHS'),
        'mat_others': fields.boolean('Others'),
        'mat_remarks': fields.text('Material Standards Remarks'),
    }
    
    _defaults = {
        'type' : 'consu',
        'name': '',
        'type': 'product',
        'procure_method': 'make_to_order',
    }
    
    _order = 'default_code,name,variants'
    
    #def print_size(self, cr, uid, ids, context=None):
        
        #for obj in self.browse(cr, uid, ids, context=context):
            #print "Image: ", len(obj.image or '')
            #print "Image small: ", len(obj.image_small or '')
            #print "Image medium: ", len(obj.image_medium or '')
            
        #return True
        
    # Check if at least one of each image type in vals is in the list of image ids
    def zeeva_product_image_check(self, cr, uid, ids, vals, product_type, context=None):
        #print ids
        #print vals
        mis_images = []
        
        if product_type == 'earphone':
            for im_type in vals:
                flag = False
                
                for image in ids:
                    #print im_type
                    #print image
                    #print image[2]
                    if im_type == image[2]['view_type_earphone_finished']: flag = True
                    
                if not flag: # No image found of type "im_type"
                    mis_images += [im_type]
                    
        elif product_type == 'headphone':
            for im_type in vals:
                flag = False
                
                for image in ids:
                    if im_type == image[2]['view_type_headphone_finished']: flag = True
                    
                if not flag: # No image found of type "im_type"
                    mis_images += [im_type]
        
        elif product_type == 'speaker':
            for im_type in vals:
                flag = False
                
                for image in ids:
                    if im_type == image[2]['view_type_speaker_finished']: flag = True
                    
                if not flag: # No image found of type "im_type"
                    mis_images += [im_type]
                    
        else:
            True
                
        # Formating the return list
        result = ''
        for name in mis_images:
            if   name == 'a1_catalog':  result += 'Catalog image, '
            elif name == 'b1_front':    result += 'Front view, '
            elif name == 'b2_back' :    result += 'Back view, '
            elif name == 'c1_left' :    result += 'Left side view, '
            elif name == 'c2_right':    result += 'Right side view, '
            elif name == 'c3_side' :    result += 'Side view, '
            elif name == 'd1_top'  :    result += 'Top view, '
            elif name == 'd2_bottom':   result += 'Bottom view, '
            elif name == 'e1_three':    result += 'Three-quarter view, '
            elif name == 'f1_plug':     result += 'Plug view, '
            elif name == 'f2_cable':    result += 'Cable view, '
            elif name == 'f3_button':   result += 'Button view, '
            elif name == 'f4_grill':    result += 'Grill view, '
            elif name == 'g1_addons':   result += 'Add-ons view, '
            elif name == 'h1_access':   result += 'Product accessories view, '
            elif name == 'i1_pos':      result += 'Product position in package view, '
            elif name == 'j1_pfront':   result += 'Package front view, '
            elif name == 'j2_pback':    result += 'Package back view, '
                
        return result
        
    def create(self, cr, user, vals, context=None):
        warning = {}
        
        #print vals
        
        # Check if all required images are present
        req_images = [] # required views
        mis_images = '' # missing views
        
        # Check earphone fields
        if 'zeeva_categ_seq' in vals:
            if vals['zeeva_categ_seq'] in range(100,200):
                req_images = ['b1_front']
                
                # Then check the images of the raw product
                mis_images = self.zeeva_product_image_check(cr, user, vals['image_ids'], req_images, 'earphone')
                
            # Check headphone fields
            elif vals['zeeva_categ_seq'] in range(200,300):
                req_images = ['b1_front']
                
                # Then check the images of the raw product
                mis_images = self.zeeva_product_image_check(cr, user, vals['image_ids'], req_images, 'headphone')
                
            # Check speaker fields
            elif vals['zeeva_categ_seq'] in range(300,400):
                req_images = ['b1_front']
                
                # Then check the images of the raw product
                mis_images = self.zeeva_product_image_check(cr, user, vals['image_ids'], req_images, 'speaker')
                
            else:
                True
                    
        if mis_images != '': # Raise error message
            raise osv.except_osv(   _('Some of the required images are missing!'),
                                    _('Missing images are: %s') % mis_images)
                                    
            return {'warning': warning,}
        
        vals['finished_creation_user'] = user
        vals['finished_creation_date'] = fields.date.context_today(self,cr,user,context=context)

        return super(product_product,self).create(cr, user, vals, context)
        
    def copy(self, cr, uid, id, default=None, context=None):
        if context is None:
            context={}

        if not default:
            default = {}
        default = default.copy()
        product_obj = self.browse(cr, uid, id, context=None)
        print product_obj
                    
        default.update({
            'variants': '',
            'product_tmpl_id': product_obj.product_tmpl_id.id,
            'finished_creation_user': uid,
            'finished_creation_date': fields.date.context_today(self,cr,uid,context=context),
            'image_ids': False,
            
        })
                
        return super(product_product, self).copy(cr, uid, id, default=default, context=context)
        
    #def copy(self, cr, uid, id, default=None, context=None):
        #if context is None:
            #context={}

        #if not default:
            #default = {}

        ## Craft our own `<name> (copy)` in en_US (self.copy_translation()
        ## will do the other languages).
        #context_wo_lang = context.copy()
        #context_wo_lang.pop('lang', None)
        #product = self.read(cr, uid, id, ['name'], context=context_wo_lang)
        #default = default.copy()
        #default.update(name=_("%s (copy)") % (product['name']))

        #if context.get('color_variant',False):
            #fields = ['product_tmpl_id', 'active', 'variants', 'default_code',
                    #'price_margin', 'price_extra', 'color_variant']
            #data = self.read(cr, uid, id, fields=fields, context=context)
            #for f in fields:
                #if f in default:
                    #data[f] = default[f]
            #data['product_tmpl_id'] = data.get('product_tmpl_id', False) \
                    #and data['product_tmpl_id'][0]
            #del data['id']
            #return self.create(cr, uid, data)
        #else:
            #return super(product_product, self).copy(cr, uid, id, default=default,
                    #context=context)
                    
    def message_subscribe_users(self, cr, uid, ids, user_ids=None, subtype_ids=None, context=None):
        """ Wrapper on message_subscribe, using users. If user_ids is not
            provided, subscribe uid instead. """
            
        if user_ids is None:
            user_ids = [uid]
            
        #ZEEVA mod start 2013-03-18
            #TODO auto add bosses by group instead of name to allow future external user to approve a product
        boss_id = self.pool.get('res.users').search(cr, uid, ['|',('login','=','akshay'),('login','=','nitin')])
        user_ids += boss_id
        #ZEEVA mod stop 2013-03-18
        
        partner_ids = [user.partner_id.id for user in self.pool.get('res.users').browse(cr, uid, user_ids, context=context)]
        return self.message_subscribe(cr, uid, ids, partner_ids, subtype_ids=subtype_ids, context=context)
    
    def onchange_tmpl(self, cr, uid, ids, product_tmpl_id, context=None):
        result = {}
        
        if product_tmpl_id:
            product_tmpl_obj = self.pool.get('product.template').browse(cr, uid, product_tmpl_id, context=None)
            
            if product_tmpl_obj:
                
                value={
                    'zeeva_categ_seq': product_tmpl_obj.zeeva_categ_seq,
                    'type': product_tmpl_obj.type,
                    'uom_id': product_tmpl_obj.uom_id.id,
                    
                    'earphone_impedance': product_tmpl_obj.earphone_impedance,
                    'earphone_freq_min': product_tmpl_obj.earphone_freq_min,
                    'earphone_freq_max': product_tmpl_obj.earphone_freq_max,
                    'earphone_sensitivity': product_tmpl_obj.earphone_sensitivity,
                    'earphone_material': product_tmpl_obj.earphone_material,
                    'earphone_driver_diam': product_tmpl_obj.earphone_driver_diam,
                    'earphone_driver_type': product_tmpl_obj.earphone_driver_type,
                    'earphone_cord_length': product_tmpl_obj.earphone_cord_length,
                    'earphone_cord_type': product_tmpl_obj.earphone_cord_type,
                    'earphone_cord_addons': product_tmpl_obj.earphone_cord_addons,
                    'earphone_plug_type': product_tmpl_obj.earphone_plug_type,
                    'earphone_plug_plating': product_tmpl_obj.earphone_plug_plating,
                    
                    'headphone_impedance': product_tmpl_obj.headphone_impedance,
                    'headphone_freq_min': product_tmpl_obj.headphone_freq_min,
                    'headphone_freq_max': product_tmpl_obj.headphone_freq_max,
                    'headphone_sensitivity': product_tmpl_obj.headphone_sensitivity,
                    'headphone_band_mat1': product_tmpl_obj.headphone_band_mat1,
                    'headphone_band_mat2': product_tmpl_obj.headphone_band_mat2,
                    'headphone_joint_mat1': product_tmpl_obj.headphone_joint_mat1,
                    'headphone_joint_mat2': product_tmpl_obj.headphone_joint_mat2,
                    'headphone_shell_mat1': product_tmpl_obj.headphone_shell_mat1,
                    'headphone_shell_mat2': product_tmpl_obj.headphone_shell_mat2,
                    'headphone_driver_diam': product_tmpl_obj.headphone_driver_diam,
                    'headphone_driver_type': product_tmpl_obj.headphone_driver_type,
                    'headphone_cord_length': product_tmpl_obj.headphone_cord_length,
                    'headphone_cord_type': product_tmpl_obj.headphone_cord_type,
                    'headphone_cord_addons': product_tmpl_obj.headphone_cord_addons,
                    'headphone_plug_type': product_tmpl_obj.headphone_plug_type,
                    'headphone_plug_plating': product_tmpl_obj.headphone_plug_plating,
                    
                    'speaker_material_body': product_tmpl_obj.speaker_material_body,
                    'speaker_material_grill': product_tmpl_obj.speaker_material_grill,
                    'speaker_driver_diam': product_tmpl_obj.speaker_driver_diam,
                    'speaker_driver_type': product_tmpl_obj.speaker_driver_type,
                    'speaker_type': product_tmpl_obj.speaker_type,
                    'speaker_output_power': product_tmpl_obj.speaker_output_power,
                    'speaker_output_nb': product_tmpl_obj.speaker_output_nb,
                    'speaker_led_indicator': product_tmpl_obj.speaker_led_indicator,
                    'speaker_battery': product_tmpl_obj.speaker_battery,
                    'speaker_battery_nb': product_tmpl_obj.speaker_battery_nb,
                    'speaker_battery_capacity': product_tmpl_obj.speaker_battery_capacity,
                    'speaker_battery_rechargeable': product_tmpl_obj.speaker_battery_rechargeable,
                    'speaker_battery_rechargeable_type': product_tmpl_obj.speaker_battery_rechargeable_type,
                    'speaker_ac_adaptor': product_tmpl_obj.speaker_ac_adaptor,
                    'speaker_impedance': product_tmpl_obj.speaker_impedance,
                    'speaker_bt': product_tmpl_obj.speaker_bt,
                    'speaker_bt_version': product_tmpl_obj.speaker_bt_version,
                    'speaker_bt_range': product_tmpl_obj.speaker_bt_range,
                    'speaker_bt_supplier': product_tmpl_obj.speaker_bt_supplier,
                    'speaker_aux_connector': product_tmpl_obj.speaker_aux_connector,
                    'speaker_aux_cable_length': product_tmpl_obj.speaker_aux_cable_length,
                    'speaker_aux_cable_type': product_tmpl_obj.speaker_aux_cable_type,
                    'speaker_mic': product_tmpl_obj.speaker_mic,
                    'speaker_call_answer_button': product_tmpl_obj.speaker_call_answer_button,
                    
                    'protec_phone_device': product_tmpl_obj.protec_phone_device,
                    'protec_phone_material': product_tmpl_obj.protec_phone_material,
                    'protec_phone_bumper': product_tmpl_obj.protec_phone_bumper,
                    'protec_phone_camhole': product_tmpl_obj.protec_phone_camhole,
                    'protec_phone_camhole_type': product_tmpl_obj.protec_phone_camhole_type,
                    'protec_phone_volume_type': product_tmpl_obj.protec_phone_volume_type,
                    'protec_phone_on_type': product_tmpl_obj.protec_phone_on_type,
                    'protec_music_device': product_tmpl_obj.protec_music_device,
                    'folio_size': product_tmpl_obj.folio_size,
                    'folio_device': product_tmpl_obj.folio_device,
                    'folio_material': product_tmpl_obj.folio_material,
                    'folio_attach': product_tmpl_obj.folio_attach,
                    'folio_protection': product_tmpl_obj.folio_protection,
                    'folio_camhole': product_tmpl_obj.folio_camhole,
                    'folio_stylus': product_tmpl_obj.folio_stylus,
                    'folio_functionalities': product_tmpl_obj.folio_functionalities,
                    'sleeve_size': product_tmpl_obj.sleeve_size,
                    'sleeve_device': product_tmpl_obj.sleeve_device,
                    'sleeve_material': product_tmpl_obj.sleeve_material,
                    'sleeve_zipper': product_tmpl_obj.sleeve_zipper,
                    'sleeve_zipper_type': product_tmpl_obj.sleeve_zipper_type,
                    'sleeve_pocket': product_tmpl_obj.sleeve_pocket,
                    'sleeve_pocket_type': product_tmpl_obj.sleeve_pocket_type,
                    
                    'zeeva_others': product_tmpl_obj.description,
                }
                
            result = {'value': value}
        
        return result
        
    def product_spec_check(self, cr, uid, ids, product, context=None):
        #desc:      Function to check if the product's mandatory fields for the Spec. Sheet report are all filled up
        #parameter: product ID
        #return:    the product name and a message with all the missing fields
        
        product_obj = self.browse(cr,uid,product,context=None)
        
        name = product_obj.default_code
        message = ""
        
        ### 1: check product fields
        if product_obj.zeeva_categ_seq in range(100,200):       #Earphones
            #RAW FIELDS CHECK
            if not product_obj.earphone_impedance: message += "Impedance, "
            if not product_obj.earphone_freq_min: message += "Frequence min, "
            if not product_obj.earphone_freq_max: message += "Frequence max, "
            if not product_obj.earphone_sensitivity: message += "Sensitivity, "
            if not product_obj.earphone_material: message += "Material, "
            if not product_obj.earphone_driver_diam: message += "Driver diameter, "
            if not product_obj.earphone_driver_type: message += "Driver type, "
            if not product_obj.earphone_cord_length: message += "Cord length, "
            if not product_obj.earphone_cord_type: message += "Cord type, "
            if not product_obj.earphone_cord_addons: message += "Cord add-ons, "
            if not product_obj.earphone_plug_type: message += "Plug type, "
            if not product_obj.earphone_plug_plating: message += "Plug plating, "
            
            #COSMETICS FIELDS CHECK
            if not product_obj.ep_housing_finish: message += "Housing finish, "
            if not product_obj.ep_logo: message += "Logo, "
            if product_obj.ep_logo == 'yes':
                if not product_obj.ep_logo_name: message += "Logo name, "
                if not product_obj.ep_logo_position: message += "Logo position, "
                
            if not product_obj.ep_printing: message += "Graphic printing, "
            if product_obj.ep_printing == 'yes':
                if not product_obj.ep_printing_type: message += "Graphic printing type, "
                if not product_obj.ep_printing_desc: message += "Graphic description, "
                
            if not product_obj.ep_packaging_type: message += "Packaging type, "
            
            #if not product_obj.: message += ", "
            
        elif product_obj.zeeva_categ_seq in range(200,300):     #Headphones
            #RAW FIELDS CHECK
            if not product_obj.headphone_impedance: message += "Impedance, "
            if not product_obj.headphone_freq_min: message += "Frequence min, "
            if not product_obj.headphone_freq_max: message += "Frequence max, "
            if not product_obj.headphone_sensitivity: message += "Sensitivity, "
            if not product_obj.headphone_band_mat1: message += "Headband material, "
            if not product_obj.headphone_joint_mat1: message += "Joints material, "
            if not product_obj.headphone_shell_mat1: message += "Shells material, "
            if not product_obj.headphone_driver_diam: message += "Driver diameter, "
            if not product_obj.headphone_driver_type: message += "Driver type, "
            
            if product_obj.zeeva_categ_seq not in [206,208]: #not wireless
                if not product_obj.headphone_cord_length: message += "Cord lenght, "
                if not product_obj.headphone_cord_type: message += "Cord type, "
                if not product_obj.headphone_cord_addons: message += "Cord add-ons, "
                if not product_obj.headphone_plug_type: message += "Plug type, "
                if not product_obj.headphone_plug_plating: message += "Plug plating, "
                
            #COSMETICS FIELDS CHECK
            if not product_obj.hp_housing_finish: message += "Housing finish, "
            if not product_obj.hp_logo: message += "Logo, "
            if product_obj.hp_logo == 'yes':
                if not product_obj.hp_logo_name: message += "Logo name, "
                if not product_obj.hp_logo_position: message += "Logo position, "
                
            if not product_obj.hp_printing: message += "Graphic printing, "
            if product_obj.hp_printing == 'yes':
                if not product_obj.hp_printing_type: message += "Graphic printing type, "
                if not product_obj.hp_printing_desc: message += "Graphic description, "
                
            if not product_obj.hp_packaging_type: message += "Packaging type, "
            if not product_obj.hp_accent_stitching: message += "Accent stitching, "
            if not product_obj.hp_deco_addons: message += "Decorative add-ons, "
            
            #if not product_obj.: message += ", "
            
        elif product_obj.zeeva_categ_seq in range(300,400):     #Speakers
            #RAW FIELDS CHECK
            if not product_obj.speaker_type:                    message += "Speaker type, "
            if not product_obj.speaker_material_body:           message += "Body material, "
            if not product_obj.speaker_material_grill:          message += "Grill material, "
            if not product_obj.speaker_driver_type:             message += "Driver type, "
            if not product_obj.speaker_driver_diam:             message += "Driver diameter, "
            if not product_obj.speaker_impedance:               message += "Impedance, "
            if not product_obj.speaker_output_power:            message += "Speaker power, "
            if not product_obj.speaker_output_nb:               message += "Speaker quantity, "
            
            if not product_obj.speaker_battery:                 message += "Battery type, "
            if product_obj.speaker_battery == 'liion':
                if not product_obj.speaker_battery_capacity: message += "Battery capacity, "
            if product_obj.speaker_battery in ['3a','2a']:
                if not product_obj.speaker_battery_nb: message += "Battery quantity, "
                
            if not product_obj.speaker_battery_rechargeable:    message += "Recharge, "
            if product_obj.speaker_battery_rechargeable == 'yes':
                if not product_obj.speaker_battery_rechargeable_type: message += "Recharge type, "
                
            if not product_obj.speaker_ac_adaptor:              message += "AC adaptor, "
            
            if not product_obj.speaker_bt:                      message += "Bluetooth, "
            if product_obj.speaker_bt == 'yes':
                if not product_obj.speaker_bt_version:              message += "BT version, "
                if not product_obj.speaker_bt_range:                message += "BT range, "
                if not product_obj.speaker_bt_supplier:             message += "BT supplier, "
                
            if not product_obj.speaker_aux_connector:           message += "AUX connector, "
            if product_obj.speaker_aux_connector == 'yes':
                if not product_obj.speaker_aux_cable_length:        message += "AUX cable length, "
                if not product_obj.speaker_aux_cable_type:          message += "AUX type"
                
            if not product_obj.speaker_mic:                     message += "Microphone, "
            if not product_obj.speaker_call_answer_button:      message += "Call answer button, "
            if not product_obj.speaker_led_indicator:           message += "LED indicator, "
            
            #COSMETICS FIELDS CHECK
            #TODO
            
        elif product_obj.zeeva_categ_seq in [401,402]:          #Device protectors
            #RAW FIELDS CHECK
            #TODO
            
            #COSMETICS FIELDS CHECK
            #TODO
            
            pass
        
        elif product_obj.zeeva_categ_seq == 403:                #Folios
            #RAW FIELDS CHECK
            #TODO
            
            #COSMETICS FIELDS CHECK
            #TODO
            
            pass
        
        elif product_obj.zeeva_categ_seq == 404:                #Sleeves
            #RAW FIELDS CHECK
            #TODO
            
            #COSMETICS FIELDS CHECK
            #TODO
            
            pass
        
        elif product_obj.zeeva_categ_seq == 425:                #Screen protectors
            #RAW FIELDS CHECK
            #TODO
            
            #COSMETICS FIELDS CHECK
            #TODO
            
            pass
        
        elif product_obj.zeeva_categ_seq in range(400,450):     #Other protectors (later)
            #RAW FIELDS CHECK
            #TODO
            
            #COSMETICS FIELDS CHECK
            #TODO
            
            pass
        
        elif product_obj.zeeva_categ_seq == 450:                #Chargers
            #RAW FIELDS CHECK
            #TODO
            
            #COSMETICS FIELDS CHECK
            #TODO
            
            pass
        
        elif product_obj.zeeva_categ_seq == 475:                #Power banks
            #RAW FIELDS CHECK
            #TODO
            
            #COSMETICS FIELDS CHECK
            #TODO
            
            pass
        
        elif product_obj.zeeva_categ_seq in range(451,1000):    #Others (TODO)
            #RAW FIELDS CHECK
            #TODO
            
            #COSMETICS FIELDS CHECK
            #TODO
            
            pass
        
        else:
            pass
        
        ### 2: check product standards
        if not product_obj.inspection_std: message += "Inspection Standard, "
        if not (product_obj.mat_rohs or product_obj.mat_cpsia or product_obj.mat_prop65 or product_obj.mat_reach or product_obj.mat_en71 or product_obj.mat_astm or product_obj.mat_pahs or product_obj.mat_others):
            message += "NO Material Standards defined, "
        
        return name, message
        
product_product()

class product_supplierinfo(osv.osv):
    _inherit = 'product.supplierinfo'
    
    _columns = {
        'sup_code': fields.related('name', 'ref', string="Supplier Code", type='char', size=64),
    }
    
    _defaults = {
    }
    
    _order = 'sequence'
product_supplierinfo()

class pricelist_partnerinfo(osv.osv):
    _inherit = 'pricelist.partnerinfo'
    
    _columns = {
        'zeeva_speaker_quality': fields.selection([('1','Tier 1'),('2','Tier 2'),('3','Tier 3')], 'Speaker quality'),
        'zeeva_date': fields.date('Date'),
    }
    
    _defaults = {
    }
    
    _order = 'zeeva_date desc, min_quantity asc'
pricelist_partnerinfo()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
